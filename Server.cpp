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
		|| line == "PART" || line == "PRIVMSG" || line == "KICK"
		|| line == "INVITE" || line == "TOPIC" || line == "MODE" || line == "CAP");
}

// TODO: Check function if it works correctly
std::vector<std::string>	Server::split_arguments(const std::string &line)
{
	std::vector<std::string>	arguments;
	size_t						start = line.find(" ");
	
	if (start == std::string::npos)
		return (arguments);

	while (start < line.length() && line[start] == ' ')
		start++;	

	while (start < line.length())
	{
		size_t	end = line.find(" ", start);
		if (end == std::string::npos)
		{
			arguments.push_back(line.substr(start));
			break ;			
		}
		
		arguments.push_back(line.substr(start, end - start));
		start = end + 1;
		while (start < line.length() && line[start] == ' ')
			start++;
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
void	Server::send_message_to_channel(Client &sender, const std::string &channel_name, const std::string &message)
{
	if (channels.find(channel_name) == channels.end())
	{
		send_error_reply(sender, "403", channel_name + " :No such channel");
		return ;
	}

	std::vector<Client>	members = channels[channel_name].get_members();

	std::string	message_to_send = ":" + sender.get_nickname() + "!" + sender.get_username()
						+ "@localhost PRIVMSG " + channel_name + " :" + message + "\r\n";

	for (size_t i = 0; i < members.size(); ++i)
	{
		if (members[i].get_socket() != sender.get_socket())
			send(members[i].get_socket(), message_to_send.c_str(), message_to_send.size(), 0);
	}
}

Client	*Server::find_client_by_nickname(const std::string &nickname)
{
	for (ClientMap::iterator it = clients.begin(); it != clients.end(); ++it)
	{
		if (it->second.get_nickname() == nickname)
			return (&it->second);
	}
	return (NULL);
}

void	Server::send_error_reply(Client &client, const std::string &code, const std::string &message)
{
	std::string nick = client.get_nickname();

	if (nick.empty())
		nick = "*";

	std::string reply = ":localhost " + code + " " + nick + " " + message + "\r\n";
	send(client.get_socket(), reply.c_str(), reply.size(), 0);
}

void	Server::send_message_to_user(Client &sender, const std::string &nickname, const std::string &message)
{
	Client *target = find_client_by_nickname(nickname);

	if (target == NULL)
	{
		send_error_reply(sender, "401", nickname + " :No such nick/channel");
		return ;
	}

	std::string message_to_send = ":" + sender.get_nickname() + "!" + sender.get_username()
						+ "@localhost PRIVMSG " + nickname + " :" + message + "\r\n";

	send(target->get_socket(), message_to_send.c_str(), message_to_send.size(), 0);
}

void	Server::send_welcome_message(Client &client)
{
	std::string nick = client.get_nickname();
	
	std::string welcome = ":localhost 001 " + nick + " :Welcome to ft_irc\r\n";
	send(client.get_socket(), welcome.c_str(), welcome.size(), 0);
	
	std::string yourhost = ":localhost 002 " + nick + " :Your host is localhost\r\n";
	send(client.get_socket(), yourhost.c_str(), yourhost.size(), 0);
	
	std::string created = ":localhost 003 " + nick + " :This server was created today\r\n";
	send(client.get_socket(), created.c_str(), created.size(), 0);
	
	std::string myinfo = ":localhost 004 " + nick + " localhost ft_irc 1.0 o o\r\n";
	send(client.get_socket(), myinfo.c_str(), myinfo.size(), 0);
}

void Server::handle_line(Client &client, const size_t &position)
{
	std::string	line;

	line = client.get_buffer().substr(0, position);
	client.get_buffer().erase(0, position + 2);

	std::string	command = line.substr(0, line.find(" "));
	if (is_command(command))
	{
		if (!client.get_admin_status()
			&& (command == "KICK" || command == "INVITE"
						|| command == "TOPIC" || command == "MODE"))
		{
			// TODO: Add a correct handle
			//not authorized
			return ;
		}

		//Get the arguments of the command so u can set it, maybe make a custom split function  
		std::vector<std::string>	arguments = split_arguments(line);

		// TODO: Make the functions
		if (arguments.empty())
			return ;

		if (command == "PASS")
		{
			client.set_password(arguments[0]);
			if (!client.get_register_status() && 
				!client.get_nickname().empty() && !client.get_username().empty())
			{
				client.set_register_status(true);
				std::cout << "Client " << client.get_nickname() << " registered successfully!" << std::endl;
				send_welcome_message(client);
			}
		}
		else if (command == "USER")
		{
			client.set_username(arguments[0]);
			if (!client.get_register_status() && 
				!client.get_nickname().empty() && !client.get_username().empty())
			{
				client.set_register_status(true);
				std::cout << "Client " << client.get_nickname() << " registered successfully!" << std::endl;
				send_welcome_message(client);
			}
		}
		else if (command == "NICK")
		{
			client.set_nickname(arguments[0]);
			if (!client.get_register_status() && 
				!client.get_nickname().empty() && !client.get_username().empty())
			{
				client.set_register_status(true);
				std::cout << "Client " << client.get_nickname() << " registered successfully!" << std::endl;
				send_welcome_message(client);
			}
		}
		else if (command == "JOIN")
		{
			if (client.get_register_status() == true)
			{
				if (!arguments.empty() && !arguments[0].empty())
					let_client_join_channel(arguments[0], client);
			}
		}
		else if (command == "PART" && client.get_register_status() == true)
			part_client_from_channel(client); // Do checks if its the only argument
		// else if (command == "KICK" && client.get_admin_status())
		// 	handle_kick();
		// else if (command == "INVITE" && client.get_admin_status())
		// 	handle_invite();
		// else if (command == "TOPIC" && client.get_admin_status())
		// 	handle_topic();
		// else if (command == "MODE" && client.get_admin_status())
		// 	handle_mode();
		else if (command == "CAP")
		{
			if (arguments.size() > 0)
			{
				if (arguments[0] == "LS")
				{
					std::string cap_response = ":localhost CAP * LS :\r\n";
					send(client.get_socket(), cap_response.c_str(), cap_response.size(), 0);
				}
				else if (arguments[0] == "END")
				{
					// CAP negotiation ended
				}
			}
		}
		else if (command == "PRIVMSG" && client.get_register_status() == true)
		{
			if (arguments.empty())
			{
				send_error_reply(client, "411", ":No recipient given (PRIVMSG)");
				return ;
			}

			std::string	message;
			std::string	target = arguments[0];
			size_t		position = line.find(" :");

			if (position != std::string::npos)
				message = line.substr(position + 2); //needs segfault protection
			else if (arguments.size() > 1)
				message = arguments[1];

			if (message.empty())
			{
				send_error_reply(client, "412", ":No text to send");
				return ;
			}

			if (!target.empty() && target[0] == '#')
				send_message_to_channel(client, target, message);
			else
				send_message_to_user(client, target, message);
		}
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
							clients[fds[index].fd].get_buffer().append(buffer, bytes_received);

							size_t	position = clients[fds[index].fd].get_buffer().find("\r\n");

							while (position != std::string::npos)
							{
								handle_line(clients[fds[index].fd], position);
								position = clients[fds[index].fd].get_buffer().find("\r\n");
							}

							if (clients.find(fds[index].fd) != clients.end())
								std::cout << "Received from client " << fds[index].fd << ": " << buffer << std::endl;
						}
						else if (bytes_received == 0)
						{
							close(fds[index].fd);
							clients.erase(fds[index].fd);
							fds.erase(fds.begin() + index);
							--index;
							break ;
						}
						else
						{
							if (errno == EAGAIN || errno == EWOULDBLOCK)
								break ;

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
