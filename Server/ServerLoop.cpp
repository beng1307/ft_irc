#include "Server.hpp"
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>
#include "../helpers/print.hpp"
#include "../helpers/Wire.hpp"

// IRC messages are limited to 512 bytes including the trailing CRLF.
static const size_t MAX_IRC_LINE_CONTENT_LENGTH = 510;

// Upper bound on how much unsent data we buffer for one client (analogous to
// an IRC server's "SendQ"). Guards against unbounded memory growth if a
// client never drains its receive side, while staying well above realistic
// burst sizes (e.g. large channel floods) so normal traffic is never dropped.
static const size_t MAX_OUTPUT_BUFFER_SIZE = 32 * 1024 * 1024;



static bool input_exceeds_irc_line_limit(const Wire &input) {
  size_t delimiter_position = input.find("\r\n");
  if (delimiter_position != std::string::npos)
    return delimiter_position > MAX_IRC_LINE_CONTENT_LENGTH;
  if (input.size() > MAX_IRC_LINE_CONTENT_LENGTH + 1)
    return true;
  // A final CR may be waiting for its LF in the next recv() call.
  return input.size() == MAX_IRC_LINE_CONTENT_LENGTH + 1
    && input[input.size() - 1] != '\r';
}

// Sets the socket to non-blocking mode and returns false if it fails.
bool Server::configure_socket_nonblocking(int socket) {
  // fcntl sets the socket flags to nonblocking with F_SETFL
  if (fcntl(socket, F_SETFL, O_NONBLOCK) == -1) {
    printErr("Error: fcntl failed!");
    return false;
  }
  return true;
}

// Sets the accepted client socket to nonblocking and gets added to the fds.
void Server::accept_new_client(int client_socket) {
  // Client socket flags gets set to nonblocking, otherwise the socket gets
  // closed.
  if (!configure_socket_nonblocking(client_socket)) {
    close(client_socket);
    return;
  }

  // Adds the client socket to the fds. And the event to listen for gets set to
  // POLLIN.
  add_fds(client_socket, POLLIN, 0);
  // Creates a new client for the client map, paired with the new socket.
  // we access existing socket in case FD is being reused.
  add_client(client_socket);
}

// Disconnects the client from channels, closes its socket, removes it from
// clients map and fds array.
void Server::disconnect_client(int client_fd) {
  // Remove client from all channels and erase empty channels
  Vector<Wire> empty_channels;
  for (ChannelMap::iterator it = get_channels().begin(); it != get_channels().end(); ++it) {
    it->second.remove_member(client_fd);
    if (it->second.empty())
      empty_channels.push_back(it->first);
  }
  for (size_t i = 0; i < empty_channels.size(); ++i)
    remove_channel(empty_channels[i]);

  // Erase from clients map
  remove_client(client_fd);

  // Erase from poll fds vector
  for (Vector<pollfd>::iterator it = get_fds().begin(); it != get_fds().end(); ++it) {
    if (it->fd == client_fd) {
      get_fds().erase(it);
      break;
    }
  }

  // Close the socket descriptor
  close(client_fd);
}

// Arms/disarms POLLOUT for a client's pollfd entry. Kept disarmed whenever
// there is nothing buffered, since a writable socket is almost always ready
// and would otherwise make poll() return immediately on every call.
void Server::set_pollout(int fd, bool enable) {
  for (Vector<pollfd>::iterator it = get_fds().begin(); it != get_fds().end(); ++it) {
    if (it->fd == fd) {
      if (enable)
        it->events = static_cast<short>(it->events | POLLOUT);
      else
        it->events = static_cast<short>(it->events & ~POLLOUT);
      break;
    }
  }
}

// Sends data to a client, buffering whatever the kernel socket buffer can't
// accept right now instead of silently dropping it (the previous behavior of
// send_string(), whose return value nobody checked). Arms POLLOUT so the
// event loop resumes the flush once the client is writable again.
// Also flushes buffered output when called on POLLOUT (message is empty).
void Server::send_to_client(int fd, const Wire &message) {
  Client &client = get_client(fd);
  if (!client)
    return;

  Wire &out = client.get_out_buffer();

  if (!message.empty()) {
    out += message;
    if (out.size() > MAX_OUTPUT_BUFFER_SIZE) {
      // Client isn't draining its receive side fast enough ("SendQ exceeded").
      disconnect_client(fd);
      return;
    }
  }

  if (out.empty()) {
    set_pollout(fd, false);
    return;
  }

  ssize_t sent = send(fd, out.c_str(), out.size(), MSG_NOSIGNAL);
  if (sent > 0) {
    out.erase(0, static_cast<size_t>(sent));
  } else if (sent == -1) {
    // A full kernel send buffer reports EAGAIN/EWOULDBLOCK on a
    // non-blocking socket; buffer the whole message for later.
    if (errno != EAGAIN && errno != EWOULDBLOCK) {
      // Any other error means the connection is dead. Disconnecting here
      // is safe even though this call can be nested inside a channel
      // broadcast: broadcasts iterate a temporary snapshot of member fds
      // that disconnect_client() never touches.
      disconnect_client(fd);
      return;
    }
  }

  if (out.empty())
    set_pollout(fd, false);
  else
    set_pollout(fd, true);
}

// Handles input from client.
void Server::handle_client_input(int client_fd) {
  char buffer[512];

  Client &client = get_client(client_fd);
  // Recieves the message from client and saves it into the buffer.
  int bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
  if (bytes_received == 0) {
    disconnect_client(client_fd);
    // Client closed the connection. So he has to be removed.
  } else if (bytes_received > 0) {
    buffer[bytes_received] = '\0';
    client.append_raw_buffer(buffer, bytes_received);

    // If the end of a message is found, it gets processed.
    size_t position = client.get_buffer().find("\r\n");
    if (input_exceeds_irc_line_limit(client.get_buffer())) {
      // Prevent a client from retaining an unbounded incomplete input buffer.
      disconnect_client(client_fd);
      return;
    }
    while (position != std::string::npos) {
      handle_line(client, position);
      // If client was disconnected by QUIT or error during handle_line, stop processing immediately
      if (!get_client(client_fd))
        return;
      position = client.get_buffer().find("\r\n");
      if (input_exceeds_irc_line_limit(client.get_buffer())) {
        disconnect_client(client_fd);
        return;
      }
    }

    print("Received from client ", client_fd, ": ", buffer);
  } else {
    // With a non-blocking socket, recv() can return -1 with
    // EAGAIN/EWOULDBLOCK if no data is currently available.
    // The client stays connected and we return to poll().
    if (errno == EAGAIN || errno == EWOULDBLOCK)
      return;
    disconnect_client(client_fd);
  }
}

// The main logic and loop of the server.
void Server::server_loop() {
  // Makes the server socket nonblocking.
  if (!configure_socket_nonblocking(get_server_socket()))
    return;

  // Adds the server socket to the fds, after
  // its flag got changed to nonblocking.
  add_fds(get_server_socket(), POLLIN, 0);

  while (g_running) {
    // Wait for events on the file descriptors (-1 == endlessly).
    // poll sets the revents flag from the fds to the current status.
    // If poll() is interrupted by a signal, it breaks the loop.
    // Otherwise, stop the server if poll() fails.
    int ready = poll(get_fds().data(), get_fds().size(), -1);
    if (ready == -1) {
      if (errno == EINTR) {
        if (!g_running)
          break;
        continue;
      }
      printErr("Error: poll failed!");
      break;
    }

    // Snapshot the fds/revents for this cycle before reacting to any of
    // them: reacting to one fd (a broadcast that overflows another client's
    // SendQ, a POLLOUT flush that errors out) can disconnect other clients
    // and mutate the live fds vector, which would corrupt index-based
    // iteration directly over it.
    Vector<pollfd> snapshot = get_fds();

    for (size_t index = 0; index < snapshot.size() && g_running; ++index) {
      int fd = snapshot[index].fd;
      short revents = snapshot[index].revents;
      bool is_server_socket = (fd == get_server_socket());
      Client &client = get_client(fd);

      // Skip fds already closed earlier in this same poll cycle.
      if (!is_server_socket && !client)
        continue;

      if (revents & (POLLERR | POLLHUP | POLLNVAL)) {
        if (is_server_socket) {
          printErr("Error: server socket poll failure!");
          break;
        }
        disconnect_client(fd);
        continue;
      }

      // A writable client socket: flush whatever output is still queued.
      if (revents & POLLOUT)
        // tells us client might be ready to receive again
        client.send(); // flush cached messages in buffer

      // The flush above may have disconnected the client on a hard error.
      if (!is_server_socket && !get_client(fd))
        continue;

      // If the current fd doesn't have POLLIN (pending input) set, go to the
      // next one.
      if (!(revents & POLLIN))
        continue;

      // If the fd has POLLIN set and is the server_socket, it means a client
      // wants to connect.
      if (is_server_socket) {
        // Client gets accepted and gets a own socket, connected to the server
        // socket.
        int client_socket = accept(get_server_socket(), NULL, NULL);
        if (client_socket == -1) {
          printErr("Error: accept failed!");
          continue;
        }
        // Handles the freshly accepted, new client.
        accept_new_client(client_socket);
      } else {
        // Handles the incoming input of the current client.
        handle_client_input(fd);
      }
    }
  }

  while (!get_clients().empty())
    disconnect_client(get_clients().begin()->first);
  if (get_server_socket() > 0) {
    close(get_server_socket());
    set_server_socket(-1);
  }
}

