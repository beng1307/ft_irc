#include "Server.hpp"
#include "Client.hpp"
#include <sys/socket.h>
#include <string>
#include <iostream>
#include <netinet/in.h>
#include <fcntl.h>
#include <poll.h>
#include <cerrno>
#include <unistd.h>

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

Server::Server(const Server &other): port(other.port), password(other.password)
{
	return ;
}

Server	&Server::operator=(const Server &other)
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


void	Server::add_fds(int fd, short events, short revents)
{
	pollfd poll_filedescriptor;

	poll_filedescriptor.fd = fd;
	poll_filedescriptor.events = events;
	poll_filedescriptor.revents = revents;

	fds.push_back(poll_filedescriptor);
}

void	Server::server_loop()
{
	//Makes the Server nonblocking by saving the flags and add O_NONBLOCK to the flags.
	int flags = fcntl(server_socket, F_GETFL, 0);
	if (flags == -1)
	{
		std::cerr << "Error: fcntl failed!" << std::endl;
		return;
	}

	if (fcntl(server_socket, F_SETFL, flags | O_NONBLOCK) == -1)
	{
		std::cerr << "Error: fcntl failed!" << std::endl;
		return;
	}

	//Adds the server socket to the poll file descriptors
	add_fds(server_socket, POLLIN, 0);

	while (true)
	{
		int ready = poll(fds.data(), fds.size(), -1);
		if (ready == -1)
		{
			if (errno == EINTR)
				continue;
			std::cerr << "Error: poll failed!" << std::endl;
			break;
		}

		for (size_t i = 0; i < fds.size(); ++i)
		{
			if (fds[i].revents & POLLIN)
			{
				if (fds[i].fd == server_socket)
				{
					int client_socket = accept(server_socket, NULL, NULL);
					if (client_socket == -1)
					{
					    std::cerr << "Error: accept failed!" << std::endl;
					    continue;
					}

					if (fcntl(client_socket, F_SETFL, flags | O_NONBLOCK) == -1)
					{
					    std::cerr << "Error: fcntl failed!" << std::endl;
					    close(client_socket);
					    continue;
					}

					add_fds(client_socket, POLLIN, 0);
					clients.insert(std::make_pair(client_socket, Client(client_socket)));
				}
				else
				{
					char	buffer[512];
					int		bytes_received = recv(fds[i].fd, buffer, sizeof(buffer) - 1, 0);
					if (bytes_received > 0)
					{
						buffer[bytes_received] = '\0';
						if (clients.find(fds[i].fd) != clients.end())
						{
							std::cout << "Received from client " << fds[i].fd << ": " << buffer << std::endl;
						}
					}
				}
			}
		}
	}
}
