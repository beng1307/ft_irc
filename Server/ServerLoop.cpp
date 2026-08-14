#include "Server.hpp"
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <iostream>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>

// Sets the socket to non-blocking mode and returns false if it fails.
bool Server::configure_socket_nonblocking(int socket) {
  // fcntl sets the socket flags to nonblocking with F_SETFL
  if (fcntl(socket, F_SETFL, O_NONBLOCK) == -1) {
    std::cerr << "Error: fcntl failed!" << std::endl;
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
  get_clients()[client_socket] = Client(client_socket);
}

// Disconnects the client from channels, closes its socket and removes it from
// the server. Decrements the index so the next client is not skipped.
void Server::disconnect_client(int client_fd, size_t &index) {
  cleanup_client_disconnect(client_fd);
  close(client_fd);
  get_clients().erase(client_fd);
  get_fds().erase(get_fds().begin() + index);
  --index;
}

// Handles input from client.
void Server::handle_client_input(int client_fd, size_t &index) {
  char buffer[512];

  // Recieves the message from client and saves it into the buffer.
  int bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
  if (bytes_received > 0) {
    // Nullterminates the message in the buffer, deklares the current client
    // and appends the buffer to the Clients buffer.
    buffer[bytes_received] = '\0';
    Client &client = get_clients()[client_fd];
    client.get_buffer().append(buffer, bytes_received);

    // If the end of a message is found, it gets processed.
    size_t position = client.get_buffer().find("\r\n");
    while (position != std::string::npos) {
      handle_line(client, position);
      position = client.get_buffer().find("\r\n");
    }

    std::cout << "Received from client " << client_fd << ": " << buffer
              << std::endl;
  } else if (bytes_received == 0) {
    // Client closed the connection. So he has to be removed.
    disconnect_client(client_fd, index);
  } else {
    // With a non-blocking socket, recv() can return -1 with
    // EAGAIN/EWOULDBLOCK if no data is currently available.
    // The client stays connected and we return to poll().
    if (errno == EAGAIN || errno == EWOULDBLOCK)
      return;
    disconnect_client(client_fd, index);
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

  while (true) {
    // Wait for events on the file descriptors (-1 == endlessly).
    // poll sets the revents flag from the fds to the current status.
    // If poll() is interrupted by a signal, it breaks the loop.
    // Otherwise, stop the server if poll() fails.
    int ready = poll(get_fds().data(), get_fds().size(), -1);
    if (ready == -1) {
      if (errno == EINTR)
        continue;
      std::cerr << "Error: poll failed!" << std::endl;
      break; // TODO: Check if it has to send a message to the clients.
    }

    // Loops over the fds
    for (size_t index = 0; index < get_fds().size(); ++index) {
      // If the current fd doesn't have POLLIN (pending input) set, go to the
      // next one.
      if (!(get_fds()[index].revents & POLLIN))
        continue;

      // If the fd has POLLIN set and is the server_socket, it means a client
      // wants to connect.
      if (get_fds()[index].fd == get_server_socket()) {
        // Client gets accepted and gets a own socket, connected to the server
        // socket.
        int client_socket = accept(get_server_socket(), NULL, NULL);
        if (client_socket == -1) {
          std::cerr << "Error: accept failed!" << std::endl;
          continue;
        }
        // Handles the freshly accepted, new client.
        accept_new_client(client_socket);
      } else
        // Handles the incoming input of the current client.
        handle_client_input(get_fds()[index].fd, index);
    }
  }
}
