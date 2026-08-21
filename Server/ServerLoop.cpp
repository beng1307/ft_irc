#include "Server.hpp"
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <unistd.h>
#include "../helpers/print.hpp"
#include "../helpers/Wire.hpp"

// IRC messages are limited to 512 bytes including the trailing CRLF.
static const size_t MAX_IRC_LINE_CONTENT_LENGTH = 510;

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

// Sets the accepted client socket to nonblocking and registers it with epoll.
void Server::accept_new_client(int client_socket) {
  // Client socket flags gets set to nonblocking, otherwise the socket gets
  // closed.
  if (!configure_socket_nonblocking(client_socket)) {
    close(client_socket);
    return;
  }

  // Adds the client socket to epoll listening for EPOLLIN.
  add_epoll_fd(client_socket, EPOLLIN);
  // Creates a new client for the client map, paired with the new socket.
  // We access existing socket in case FD is being reused.
  add_client(client_socket);
}

// Disconnects the client from channels, closes its socket, removes it from
// clients map and epoll instance.
void Server::disconnect_client(int client_fd) {
  // Remove client from all channels and erase empty channels
  for (ChannelMap::iterator it = get_channels().begin(); it != get_channels().end();) {
    it->second.remove_member(client_fd);
    if (it->second.empty())
      get_channels().erase(it++);
    else
      ++it;
  }

  // Erase from clients map
  remove_client(client_fd);

  // Remove from epoll
  remove_epoll_fd(client_fd);

  // Close the socket descriptor
  close(client_fd);
}

// Handles input from client.
void Server::handle_client_input(int client_fd) {
  char buffer[512];

  // Receives the message from client and saves it into the buffer.
  int bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
  if (bytes_received > 0) {
    // Nullterminates the message in the buffer, declares the current client
    // and appends the buffer to the Clients buffer.
    buffer[bytes_received] = '\0';
    Client &client = get_clients()[client_fd];
    client.get_buffer().append(buffer, bytes_received);

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
  } else if (bytes_received == 0) {
    // Client closed the connection. So he has to be removed.
    disconnect_client(client_fd);
  } else {
    // With a non-blocking socket, recv() can return -1 with
    // EAGAIN/EWOULDBLOCK if no data is currently available.
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

  // Creates the epoll instance to monitor file descriptors.
  int epfd = epoll_create1(0);
  if (epfd == -1) {
    printErr("Error: epoll_create1 failed!");
    return;
  }
  set_epoll_fd(epfd);

  // Adds the server socket to epoll to listen for incoming connections (EPOLLIN),
  // after its flag got changed to nonblocking.
  add_epoll_fd(get_server_socket(), EPOLLIN);

  const int MAX_EVENTS = 64;
  struct epoll_event events[MAX_EVENTS];

  while (g_running) {
    // Wait for events on registered file descriptors (-1 == endlessly).
    // epoll_wait fills the events array with only the file descriptors that have triggered events.
    // If epoll_wait() is interrupted by a signal, it unblocks with EINTR and continues or breaks the loop.
    // Otherwise, stop the server if epoll_wait() fails.
    int nfds = epoll_wait(get_epoll_fd(), events, MAX_EVENTS, -1);
    if (nfds == -1) {
      if (errno == EINTR) {
        if (!g_running)
          break;
        continue;
      }
      printErr("Error: epoll_wait failed!");
      break;
    }

    // Loops over only the active/ready file descriptors returned by epoll_wait.
    for (int i = 0; i < nfds && g_running; ++i) {
      int current_fd = events[i].data.fd;
      uint32_t ev = events[i].events;

      // Checks for error or hangup events on the file descriptor.
      if (ev & (EPOLLERR | EPOLLHUP)) {
        if (current_fd == get_server_socket()) {
          printErr("Error: server socket epoll failure!");
          break;
        }
        // Disconnects and cleans up the client associated with the failed socket.
        disconnect_client(current_fd);
        continue;
      }

      // If the current fd has EPOLLIN (pending input or incoming connection) set.
      if (ev & EPOLLIN) {
        // If the fd is the server_socket, it means a new client wants to connect.
        if (current_fd == get_server_socket()) {
          // Client gets accepted and gets its own socket, connected to the server socket.
          int client_socket = accept(get_server_socket(), NULL, NULL);
          if (client_socket == -1) {
            printErr("Error: accept failed!");
            continue;
          }
          // Handles and registers the freshly accepted, new client.
          accept_new_client(client_socket);
        } else {
          // Handles the incoming input of the current connected client.
          handle_client_input(current_fd);
        }
      }
    }
  }

  // Gracefully disconnects all remaining clients upon server shutdown.
  while (!get_clients().empty())
    disconnect_client(get_clients().begin()->first);

  // Closes the server listening socket descriptor.
  if (get_server_socket() > 0) {
    close(get_server_socket());
    set_server_socket(-1);
  }

  // Closes the epoll instance file descriptor.
  if (get_epoll_fd() >= 0) {
    close(get_epoll_fd());
    set_epoll_fd(-1);
  }
}
