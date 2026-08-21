#include "Server.hpp"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "../helpers/print.hpp"

// Sets up the master listening TCP socket:
// 1. Creates IPv4 TCP stream socket (socket(AF_INET, SOCK_STREAM, 0))
// 2. Configures SO_REUSEADDR to enable immediate address reuse after server restart
// 3. Initializes sockaddr_in (htons port conversion, INADDR_ANY interface binding)
// 4. Binds socket to specified port and puts it in listening state (backlog = 5)
//
// Failure Handling Rationale:
// If setsockopt, bind, or listen fails (e.g. EADDRINUSE if port is occupied, EACCES if <1024 without root),
// we explicitly close(get_server_socket()) and reset to -1 before returning 1.
// Otherwise, an open un-bound / un-listening socket FD leaks and if passed into poll(),
// causes poll() to block indefinitely without accepting any traffic.
int	Server::socket_setup()
{
	// Creates a socket
	// AF_INET: IPv4, SOCK_STREAM: TCP stream, 0: default protocol
	int sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock == -1)
	{
		set_server_socket(Fd());
		printErr("Error: socket creation failed!");
		return (1);
	}
	set_server_socket(sock);

	// Sets the socket options to allow fast reuse of the address and port
	// Scenario: Server restarts immediately after shutdown while previous sockets may linger in kernel TIME_WAIT.
	// Rationale: Avoids bind() failing with "Address already in use" (EADDRINUSE) during quick test restarts.
	int on = 1;
	if (setsockopt(get_server_socket(), SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) == -1)
	{
		printErr("Error: setsockopt failed!");
		close(get_server_socket());
		set_server_socket(Fd());
		return (1);
	}

	// Initializes the server address structure
	// htons converts the port number from host byte order to network byte order (Big Endian)
	// INADDR_ANY allows the server to accept connections on any IP address / network interface of the host machine (0.0.0.0)
	sockaddr_in	server_addr;

	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(get_port());
	server_addr.sin_addr.s_addr = INADDR_ANY;

	// Binds the socket to the specified port and address
	// Scenario: Fails if port is already in use by another process (EADDRINUSE)
	// or if a privileged port < 1024 is requested without root privileges (EACCES).
	if (bind(get_server_socket(), reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) == -1)
	{
		printErr("Error: bind failed!");
		close(get_server_socket());
		set_server_socket(Fd());
		return (1);
	}

	// Puts the server socket into listening mode, allowing it to accept incoming connection requests
	// Backlog of 5 defines the maximum queue length for pending incompletely established (SYN) connections.
	if (listen(get_server_socket(), 5) == -1)
	{
		printErr("Error: listen failed!");
		close(get_server_socket());
		set_server_socket(Fd());
		return (1);
	}

	return (0);
}