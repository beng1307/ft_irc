#include "Server.hpp"
#include <sys/socket.h>
#include <string>
#include <iostream>
#include <netinet/in.h>


///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Server::Server()
{
	return ;
}

Server::Server(int port, std::string password): port(port), password(password)
{
	return ;
}

Server::Server(Server &other): port(other.port), password(other.password)
{
	return ;
}

Server	&Server::operator=(Server &other)
{
	if (this != &other)
	{
		port = other.port;
		password = other.password;
	}
	return (*this);
}


///////////////////////////////////////////////////////////////////////////////
// Methods

int	Server::socket_setup()
{
	//Creates a socket
	//AF_INET: IPv4, SOCK_STREAM: TCP, 0: default protocol
	server_socket = socket(AF_INET, SOCK_STREAM, 0);
	if (server_socket == -1)
	{
		std::cerr << "Error: socket creation failed!"<< std::endl;
		return (1);
	}

	//Sets the socket options to allow fast reuse of the address and port
	int on = 1;
	if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) == -1)
	{
		std::cerr << "Error: setsockopt failed!"<< std::endl;
		return (1);
	}

	//Initializes the server address structure
	//htons converts the port number from host byte order to network byte order
	//INADDR_ANY allows the server to accept connections on any IP address of the host machine
	sockaddr_in	server_addr;

	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(port);
	server_addr.sin_addr.s_addr = INADDR_ANY;

	//Binds the socket to the specified port and address
	if (bind(server_socket, reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) == -1)
	{
		std::cerr << "Error: bind failed!"<< std::endl;
		return (1);
	}

	//Puts the server socket into listening mode, allowing it to accept incoming connection requests
	if (listen(server_socket, 5) == -1)
	{
		std::cerr << "Error: listen failed!"<< std::endl;
		return (1);
	}

	return (0);
}

void	Server::server_loop()
{

}
