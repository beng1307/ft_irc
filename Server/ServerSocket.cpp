#include "Server.hpp"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "../helpers/print.hpp"

int	Server::socket_setup()
{
	//Creates a socket
	//AF_INET: IPv4, SOCK_STREAM: TCP, 0: default protocol
	set_server_socket(socket(AF_INET, SOCK_STREAM, 0));
	if (get_server_socket() == -1)
	{
		printErr("Error: socket creation failed!");
		return (1);
	}

	//Sets the socket options to allow fast reuse of the address and port
	int on = 1;
	if (setsockopt(get_server_socket(), SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) == -1)
	{
		printErr("Error: setsockopt failed!");
		return (1);
	}

	//Initializes the server address structure
	//htons converts the port number from host byte order to network byte order
	//INADDR_ANY allows the server to accept connections on any IP address of the host machine
	sockaddr_in	server_addr;

	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(get_port());
	server_addr.sin_addr.s_addr = INADDR_ANY;

	//Binds the socket to the specified port and address
	if (bind(get_server_socket(), reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) == -1)
	{
		printErr("Error: bind failed!");
		return (1);
	}

	//Puts the server socket into listening mode, allowing it to accept incoming connection requests
	if (listen(get_server_socket(), 5) == -1)
	{
		printErr("Error: listen failed!");
		return (1);
	}

	return (0);
}