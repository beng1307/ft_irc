#include "Server.hpp"
#include "Client.hpp"
#include "Channel.hpp"
#include <sys/socket.h>
#include <string>
#include <iostream>
#include <netinet/in.h>
#include <fcntl.h>
#include <poll.h>
#include <cerrno>
#include <unistd.h>
#include <algorithm>
#include <vector>

// TODO: Make more comments on the functions

///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Server::Server()
{
	return ;
}

Server::Server(int port, std::string password):
	port(port), password(password), server_socket(0), clients(), channels(), fds()
{
	return ;
}

Server::Server(const Server &other): port(other.port), password(other.password),
	server_socket(other.server_socket), clients(other.clients), channels(other.channels), fds(other.fds)
{
	return ;
}

Server	&Server::operator=(const Server &other)
{
	if (this != &other)
	{
		port = other.port;
		password = other.password;
		server_socket = other.server_socket;
		clients = other.clients;
		channels = other.channels;
		fds = other.fds;
	}
	return (*this);
}

Server::~Server()
{
	return ;
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

// TODO: Add comments
void	Server::add_fds(int fd, short events, short revents)
{
	pollfd poll_filedescriptor;

	poll_filedescriptor.fd = fd;
	poll_filedescriptor.events = events;
	poll_filedescriptor.revents = revents;

	fds.push_back(poll_filedescriptor);
}

bool	Server::is_command(const std::string &line)
{
	return (line == "PASS" || line == "USER" || line == "NICK" || line == "JOIN" 
		|| line == "KICK" || line == "INVITE" || line == "TOPIC" || line == "MODE");
}

// TODO: Check function if it works correctly
std::vector<std::string>	Server::split_arguments(const std::string &line)
{
	std::vector<std::string>	arguments;
	size_t						start = line.find(" ");
	
	if (start == std::string::npos)
		return (arguments);

	while (line[start] == ' ')
		start++;	

	size_t	end = start;
	while (end != std::string::npos)
	{
		while (line[start] == ' ')
			start++;
		
		end = line.find(" ", start);
		if (end == std::string::npos)
		{
			arguments.push_back(line.substr(start));
			break ;			
		}
		
		arguments.push_back(line.substr(start, end - start));
	}
	
	return (arguments);
}

// void Server::handle_kick()
// {
// }

// void Server::handle_invite()
// {
// }

// void Server::handle_topic()
// {
// }

// void Server::handle_mode()
// {
// }


//Check if this function works properly
void	Server::let_client_join_channel(const std::string &channel_name, Client &client)
{
	// Checks if the channel already exists, if not it gets created and a client gets added
	if (channels.find(channel_name) == channels.end())
	{
		channels[channel_name] = Channel(channel_name);
		std::cout << "Channel " << channel_name << " created!" << std::endl;

		channels[channel_name].add_member(client); // Check if its the correct client that gets added
		std::cout << "Client joined channel " << channel_name << "!" << std::endl;
	}
	// Else if it exisits already only the client gets added to the channel
	else
	{
		if (channels[channel_name].has_member(client))
		{
			std::cout << "Client is already in channel " << channel_name << "!" << std::endl;
			return ;
		}

		channels[channel_name].add_member(client);
		std::cout << "Client joined channel " << channel_name << "!" << std::endl;
	}
}

void	Server::part_client_from_channel(Client &client)
{
	for (ChannelMap::iterator it = channels.begin(); it != channels.end(); ++it)
	{
		if (it->second.has_member(client))
		{
			it->second.remove_member(client);
			std::cout << "Client left channel " << it->second.get_name() << "!" << std::endl;
		}
		else
			//maybe do it with Errorhandler
			std::cout << "Client is not in channel!" << std::endl;
	}
}


//TODO: send message to all clients in channel except sender
// void	Server::send_message_to_channel(const std::string &line)
// {
// }

void Server::handle_line(Client &client, const size_t &position)
{
	std::string	line;

	line = client.get_buffer().substr(0, position);
	client.get_buffer().erase(0, position + 2);

	std::string	command = line.substr(0, line.find(" "));
	if (is_command(command))
	{
		if (!client.get_admin_status()
			&& (command == "KICK" || command == "INVITE" || command == "USER"
						|| command == "TOPIC" || command == "MODE"
						|| command == "JOIN" || command == "PART"
						|| command == "PRIVMSG" || command == "PASS"))
		{
			// TODO: Add a correct handle
			//not authorized
			return ;
		}

		//Get the arguments of the command so u can set it, maybe make a custom split function  
		std::vector<std::string>	arguments = split_arguments(line);

		// TODO: Make the functions
		if (command == "PASS")
			client.set_password(arguments[0]); // Do checks if its the only argument
		else if (command == "USER")
			client.set_username(arguments[0]); // Do checks if its the only argument
		else if (command == "NICK")
			client.set_nickname(arguments[0]); // Do checks if its the only argument
		else if (command == "JOIN" && client.get_register_status() == true)
			let_client_join_channel(arguments[0], client); // Do checks if its the only argument
		else if (command == "PART" && client.get_register_status() == true)
			part_client_from_channel(client); // Do checks if its the only argument
		// else if (command == "PRIVMSG")
		// 	send_message_to_channel(line); // Do checks if its the only argument
		// else if (command == "KICK" && client.get_admin_status())
		// 	handle_kick();
		// else if (command == "INVITE" && client.get_admin_status())
		// 	handle_invite();
		// else if (command == "TOPIC" && client.get_admin_status())
		// 	handle_topic();
		// else if (command == "MODE" && client.get_admin_status())
		// 	handle_mode();
		// else
		// 	send_message_to_channel(line);
	}
}

// TODO: Split the loop into smaller functions nad add much more comments to the code
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

	// Server loop that continuously checks for events
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

		// Goes through all the file descriptors and checks if there are events to handle
		for (size_t index = 0; index < fds.size(); ++index)
		{
			if (fds[index].revents & POLLIN)
			{
				if (fds[index].fd == server_socket)
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
					char	buffer[512]; // Check if its the best approach

					while (true)
					{
						int	bytes_received = recv(fds[index].fd, buffer, sizeof(buffer) - 1, 0);
						if (bytes_received > 0)
						{
							buffer[bytes_received] = '\0';

							std::string	string_buffer(buffer);
							clients[fds[index].fd].get_buffer().append(buffer, bytes_received);

							size_t	position = clients[fds[index].fd].get_buffer().find("\r\n");
							if (position != std::string::npos)
								handle_line(clients[fds[index].fd], position);

							if (clients.find(fds[index].fd) != clients.end())
								std::cout << "Received from client " << fds[index].fd << ": " << buffer << std::endl;
						}
						// TODO: Check this statement
						else
						{
							close(fds[index].fd);
							clients.erase(fds[index].fd);
							fds.erase(fds.begin() + index);
							--index;
							break ;
						}
					}
				}
			}
		}
	}
}
