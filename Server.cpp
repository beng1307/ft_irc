#include "Server.hpp"
#include <sys/socket.h>
#include <string>

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
// Public Methods

int	Server::socket_setup()
{
	server_socket = socket(AF_INET, SOCK_STREAM, 0);

	setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR,)
}
