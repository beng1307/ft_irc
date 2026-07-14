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
#include <sstream>
#include <cctype>
#include <cstdlib>

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


///////////////////////////////////////////////////////////////////////////////
// Helper functions

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

static void	append_mode_change(std::string &applied_modes, char sign, char mode)
{
	if (applied_modes.empty() || applied_modes[applied_modes.size() - 1] != sign)
		applied_modes.push_back(sign);
	applied_modes.push_back(mode);
}

static std::string	to_string_size_t(size_t value)
{
	std::ostringstream oss;
	oss << value;
	return (oss.str());
}

static bool	is_positive_number(const std::string &value)
{
	if (value.empty())
		return (false);
	for (size_t i = 0; i < value.size(); ++i)
	{
		if (!std::isdigit(static_cast<unsigned char>(value[i])))
			return (false);
	}
	if (value == "0")
		return (false);
	return (true);
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

Client	*Server::find_client_by_nickname(const std::string &nickname)
{
	for (ClientMap::iterator it = clients.begin(); it != clients.end(); ++it)
	{
		if (it->second.get_nickname() == nickname)
			return (&it->second);
	}
	return (NULL);
}

void	Server::cleanup_client_disconnect(int disconnected_fd)
{
	for (ChannelMap::iterator it = channels.begin(); it != channels.end();)
	{
		it->second.remove_member(disconnected_fd);
		if (it->second.get_member_fds().empty())
			channels.erase(it++);
		else
			++it;
	}
}

void	Server::try_register_client(Client &client)
{
	if (client.get_register_status())
		return ;
	if (!client.get_pass_ok())
		return ;
	if (client.get_nickname().empty() || client.get_username().empty())
		return ;

	client.set_register_status(true);
	std::cout << "Client " << client.get_nickname() << " registered successfully!" << std::endl;
	send_welcome_message(client);
}

///////////////////////////////////////////////////////////////////////////////
// Command handling functions

void	Server::handle_kick(Client &client, const std::string &line,
		const std::vector<std::string> &arguments)
{
	if (arguments.size() < 2)
	{
		send_error_reply(client, "461", "KICK :Not enough parameters");
		return ;
	}

	const std::string &channel_name = arguments[0];
	const std::string &target_nick = arguments[1];

	ChannelMap::iterator channel_it = channels.find(channel_name);
	if (channel_it == channels.end())
	{
		send_error_reply(client, "403", channel_name + " :No such channel");
		return ;
	}

	if (!channel_it->second.has_member(client.get_socket()))
	{
		send_error_reply(client, "442", channel_name + " :You're not on that channel");
		return ;
	}

	if (!channel_it->second.is_operator(client.get_socket()))
	{
		send_error_reply(client, "482", channel_name + " :You're not channel operator");
		return ;
	}

	Client *target = find_client_by_nickname(target_nick);
	if (target == NULL)
	{
		send_error_reply(client, "401", target_nick + " :No such nick/channel");
		return ;
	}

	if (!channel_it->second.has_member(target->get_socket()))
	{
		send_error_reply(client, "441", target_nick + " " + channel_name
			+ " :They aren't on that channel");
		return ;
	}

	std::string reason = client.get_nickname();
	size_t reason_pos = line.find(" :");
	if (reason_pos != std::string::npos && reason_pos + 2 < line.size())
		reason = line.substr(reason_pos + 2);

	std::string kick_message = ":" + client.get_nickname() + "!" + client.get_username()
		+ "@localhost KICK " + channel_name + " " + target_nick + " :" + reason + "\r\n";

	std::set<int> member_fds = channel_it->second.get_member_fds();
	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send(*it, kick_message.c_str(), kick_message.size(), 0);

	channel_it->second.remove_member(target->get_socket());
}

void	Server::handle_invite(Client &client,
		const std::vector<std::string> &arguments)
{
	if (arguments.size() < 2)
	{
		send_error_reply(client, "461", "INVITE :Not enough parameters");
		return ;
	}

	const std::string &target_nick = arguments[0];
	const std::string &channel_name = arguments[1];

	ChannelMap::iterator channel_it = channels.find(channel_name);
	if (channel_it == channels.end())
	{
		send_error_reply(client, "403", channel_name + " :No such channel");
		return ;
	}

	if (!channel_it->second.has_member(client.get_socket()))
	{
		send_error_reply(client, "442", channel_name + " :You're not on that channel");
		return ;
	}

	if (!channel_it->second.is_operator(client.get_socket()))
	{
		send_error_reply(client, "482", channel_name + " :You're not channel operator");
		return ;
	}

	Client *target = find_client_by_nickname(target_nick);
	if (target == NULL)
	{
		send_error_reply(client, "401", target_nick + " :No such nick/channel");
		return ;
	}

	if (channel_it->second.has_member(target->get_socket()))
	{
		send_error_reply(client, "443", target_nick + " " + channel_name
			+ " :is already on channel");
		return ;
	}

	std::string invite_message = ":" + client.get_nickname() + "!" + client.get_username()
		+ "@localhost INVITE " + target_nick + " :" + channel_name + "\r\n";
	send(target->get_socket(), invite_message.c_str(), invite_message.size(), 0);

	std::string nick = client.get_nickname();
	if (nick.empty())
		nick = "*";
	std::string invite_reply = ":localhost 341 " + nick + " " + target_nick
		+ " " + channel_name + "\r\n";
	send(client.get_socket(), invite_reply.c_str(), invite_reply.size(), 0);

	channel_it->second.add_invited(target->get_socket());

}

void	Server::handle_topic(Client &client, const std::string &line,
		const std::vector<std::string> &arguments)
{
	if (arguments.size() < 1)
	{
		send_error_reply(client, "461", "TOPIC :Not enough parameters");
		return ;
	}

	const std::string &channel_name = arguments[0];
	ChannelMap::iterator channel_it = channels.find(channel_name);
	if (channel_it == channels.end())
	{
		send_error_reply(client, "403", channel_name + " :No such channel");
		return ;
	}

	if (!channel_it->second.has_member(client.get_socket()))
	{
		send_error_reply(client, "442", channel_name + " :You're not on that channel");
		return ;
	}

	size_t topic_pos = line.find(" :");
	if (topic_pos == std::string::npos)
	{
		std::string nick = client.get_nickname();
		if (nick.empty())
			nick = "*";

		std::string topic = channel_it->second.get_topic();
		if (topic.empty())
		{
			std::string no_topic_reply = ":localhost 331 " + nick + " "
				+ channel_name + " :No topic is set\r\n";
			send(client.get_socket(), no_topic_reply.c_str(), no_topic_reply.size(), 0);
		}
		else
		{
			std::string topic_reply = ":localhost 332 " + nick + " "
				+ channel_name + " :" + topic + "\r\n";
			send(client.get_socket(), topic_reply.c_str(), topic_reply.size(), 0);
		}
		return ;
	}

	if (channel_it->second.is_topic_restricted()
		&& !channel_it->second.is_operator(client.get_socket()))
	{
		send_error_reply(client, "482", channel_name + " :You're not channel operator");
		return ;
	}

	std::string new_topic = line.substr(topic_pos + 2);
	channel_it->second.set_topic(new_topic);

	std::string topic_message = ":" + client.get_nickname() + "!" + client.get_username()
		+ "@localhost TOPIC " + channel_name + " :" + new_topic + "\r\n";

	std::set<int> member_fds = channel_it->second.get_member_fds();
	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send(*it, topic_message.c_str(), topic_message.size(), 0);
}
void	Server::handle_mode(Client &client, const std::string &line,
		const std::vector<std::string> &arguments)
{
	(void)line;
	if (arguments.empty())
	{
		send_error_reply(client, "461", "MODE :Not enough parameters");
		return ;
	}

	const std::string &channel_name = arguments[0];
	ChannelMap::iterator channel_it = channels.find(channel_name);
	if (channel_it == channels.end())
	{
		send_error_reply(client, "403", channel_name + " :No such channel");
		return ;
	}

	if (!channel_it->second.has_member(client.get_socket()))
	{
		send_error_reply(client, "442", channel_name + " :You're not on that channel");
		return ;
	}

	std::string nick = client.get_nickname();
	if (nick.empty())
		nick = "*";

	if (arguments.size() == 1)
	{
		std::string current_modes = "+";
		std::vector<std::string> current_params;

		if (channel_it->second.is_invite_only())
			current_modes.push_back('i');
		if (channel_it->second.is_topic_restricted())
			current_modes.push_back('t');
		if (channel_it->second.has_key())
		{
			current_modes.push_back('k');
			current_params.push_back(channel_it->second.get_key());
		}
		if (channel_it->second.has_user_limit())
		{
			current_modes.push_back('l');
			current_params.push_back(to_string_size_t(channel_it->second.get_user_limit()));
		}

		std::string mode_reply = ":localhost 324 " + nick + " " + channel_name + " " + current_modes;
		for (size_t i = 0; i < current_params.size(); ++i)
			mode_reply += " " + current_params[i];
		mode_reply += "\r\n";
		send(client.get_socket(), mode_reply.c_str(), mode_reply.size(), 0);
		return ;
	}

	if (!channel_it->second.is_operator(client.get_socket()))
	{
		send_error_reply(client, "482", channel_name + " :You're not channel operator");
		return ;
	}

	const std::string &mode_string = arguments[1];
	char sign = 0;
	size_t param_index = 2;
	std::string applied_modes;
	std::vector<std::string> applied_params;

	for (size_t i = 0; i < mode_string.size(); ++i)
	{
		char mode = mode_string[i];
		if (mode == '+' || mode == '-')
		{
			sign = mode;
			continue ;
		}
		if (sign == 0)
			continue ;

		if (mode == 'i')
		{
			channel_it->second.set_invite_only(sign == '+');
			append_mode_change(applied_modes, sign, 'i');
		}
		else if (mode == 't')
		{
			channel_it->second.set_topic_restricted(sign == '+');
			append_mode_change(applied_modes, sign, 't');
		}
		else if (mode == 'k')
		{
			if (sign == '+')
			{
				if (param_index >= arguments.size())
				{
					send_error_reply(client, "461", "MODE :Not enough parameters");
					continue ;
				}
				channel_it->second.set_key(arguments[param_index]);
				append_mode_change(applied_modes, sign, 'k');
				applied_params.push_back(arguments[param_index]);
				param_index++;
			}
			else
			{
				if (channel_it->second.has_key())
				{
					channel_it->second.clear_key();
					append_mode_change(applied_modes, sign, 'k');
				}
			}
		}
		else if (mode == 'o')
		{
			if (param_index >= arguments.size())
			{
				send_error_reply(client, "461", "MODE :Not enough parameters");
				continue ;
			}

			const std::string &target_nick = arguments[param_index];
			Client *target = find_client_by_nickname(target_nick);
			if (target == NULL)
			{
				send_error_reply(client, "401", target_nick + " :No such nick/channel");
				param_index++;
				continue ;
			}
			if (!channel_it->second.has_member(target->get_socket()))
			{
				send_error_reply(client, "441", target_nick + " " + channel_name
					+ " :They aren't on that channel");
				param_index++;
				continue ;
			}

			if (sign == '+')
				channel_it->second.add_operator(target->get_socket());
			else
				channel_it->second.remove_operator(target->get_socket());

			append_mode_change(applied_modes, sign, 'o');
			applied_params.push_back(target_nick);
			param_index++;
		}
		else if (mode == 'l')
		{
			if (sign == '+')
			{
				if (param_index >= arguments.size() || !is_positive_number(arguments[param_index]))
				{
					send_error_reply(client, "461", "MODE :Not enough parameters");
					if (param_index < arguments.size())
						param_index++;
					continue ;
				}
				size_t limit_value = static_cast<size_t>(std::atoi(arguments[param_index].c_str()));
				channel_it->second.set_user_limit(limit_value);
				append_mode_change(applied_modes, sign, 'l');
				applied_params.push_back(arguments[param_index]);
				param_index++;
			}
			else
			{
				if (channel_it->second.has_user_limit())
				{
					channel_it->second.clear_user_limit();
					append_mode_change(applied_modes, sign, 'l');
				}
			}
		}
		else
		{
			send_error_reply(client, "472", std::string(1, mode) + " :is unknown mode char to me");
		}
	}

	if (applied_modes.empty())
		return ;

	std::string mode_message = ":" + client.get_nickname() + "!" + client.get_username()
		+ "@localhost MODE " + channel_name + " " + applied_modes;
	for (size_t i = 0; i < applied_params.size(); ++i)
		mode_message += " " + applied_params[i];
	mode_message += "\r\n";

	std::set<int> member_fds = channel_it->second.get_member_fds();
	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send(*it, mode_message.c_str(), mode_message.size(), 0);
}



///////////////////////////////////////////////////////////////////////////////
// Methods for joining and parting of the client into/from a channel

void	Server::let_client_join_channel(const std::string &channel_name, Client &client, const std::string &key)
{
	int client_fd = client.get_socket();

	// Checks if the channel already exists, if not it gets created and a client gets added
	if (channels.find(channel_name) == channels.end())
	{
		channels[channel_name] = Channel(channel_name);
		std::cout << "Channel " << channel_name << " created!" << std::endl;
 
		channels[channel_name].add_member(client_fd); // Check if its the correct client that gets added
		channels[channel_name].add_operator(client_fd);
		std::cout << "Client joined channel " << channel_name << "!" << std::endl;
		return ;
	}

	Channel &channel = channels[channel_name];

	if (channel.has_member(client_fd))
	{
		std::cout << "Client is already in channel " << channel_name << "!" << std::endl;
		return ;
	}

	if (channel.is_invite_only() && !channel.is_invited(client_fd)
		&& !channel.is_operator(client_fd))
	{
		send_error_reply(client, "473", channel_name + " :Cannot join channel (+i)");
		return ;
	}

	if (channel.has_key() && channel.get_key() != key)
	{
		send_error_reply(client, "475", channel_name + " :Cannot join channel (+k)");
		return ;
	}

	if (channel.has_user_limit()
		&& channel.get_member_fds().size() >= channel.get_user_limit())
	{
		send_error_reply(client, "471", channel_name + " :Cannot join channel (+l)");
		return ;
	}

	channel.add_member(client_fd);
	channel.remove_invited(client_fd);
	std::cout << "Client joined channel " << channel_name << "!" << std::endl;
}

void	Server::part_client_from_channel(Client &client, const std::string &channel_name)
{
	ChannelMap::iterator it = channels.find(channel_name);
	if (it == channels.end())
	{
		send_error_reply(client, "403", channel_name + " :No such channel");
		return ;
	}

	if (!it->second.has_member(client.get_socket()))
	{
		send_error_reply(client, "442", channel_name + " :You're not on that channel");
		return ;
	}

	it->second.remove_member(client.get_socket());
	std::cout << "Client left channel " << it->second.get_name() << "!" << std::endl;
}


///////////////////////////////////////////////////////////////////////////////
// Sending

void	Server::send_message_to_channel(Client &sender, const std::string &channel_name, const std::string &message)
{
	if (channels.find(channel_name) == channels.end())
	{
		send_error_reply(sender, "403", channel_name + " :No such channel");
		return ;
	}

	std::set<int>	member_fds = channels[channel_name].get_member_fds();

	std::string	message_to_send = ":" + sender.get_nickname() + "!" + sender.get_username()
						+ "@localhost PRIVMSG " + channel_name + " :" + message + "\r\n";

	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
	{
		if (*it != sender.get_socket())
			send(*it, message_to_send.c_str(), message_to_send.size(), 0);
	}
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





///////////////////////////////////////////////////////////////////////////////
// Line Handling

void Server::handle_line(Client &client, const size_t &position)
{
	std::string	line;

	line = client.get_buffer().substr(0, position);
	client.get_buffer().erase(0, position + 2);

	std::string	command = line.substr(0, line.find(" "));
	if (is_command(command))
	{
		//Get the arguments of the command so u can set it, maybe make a custom split function  
		std::vector<std::string>	arguments = split_arguments(line);

		if (command == "PASS")
		{
			if (arguments.empty())
			{
				send_error_reply(client, "461", "PASS :Not enough parameters");
				return ;
			}
			if (client.get_register_status())
			{
				send_error_reply(client, "462", ":You may not reregister");
				return ;
			}
			if (arguments[0] != password)
			{
				client.set_pass_ok(false);
				send_error_reply(client, "464", ":Password incorrect");
				return ;
			}
			client.set_password(arguments[0]);
			client.set_pass_ok(true);
			try_register_client(client);
		}
		else if (command == "USER")
		{
			if (arguments.empty())
			{
				send_error_reply(client, "461", "USER :Not enough parameters");
				return ;
			}
			if (client.get_register_status())
			{
				send_error_reply(client, "462", ":You may not reregister");
				return ;
			}
			client.set_username(arguments[0]);
			try_register_client(client);
		}
		else if (command == "NICK")
		{
			if (arguments.empty())
			{
				send_error_reply(client, "431", ":No nickname given");
				return ;
			}
			Client *existing_client = find_client_by_nickname(arguments[0]);
			if (existing_client != NULL
				&& existing_client->get_socket() != client.get_socket())
			{
				send_error_reply(client, "433", arguments[0] + " :Nickname is already in use");
				return ;
			}
			client.set_nickname(arguments[0]);
			try_register_client(client);
		}
		else if (command == "JOIN")
		{
			if (client.get_register_status() == true)
			{
				if (!arguments.empty() && !arguments[0].empty())
				{
					std::string key;
					if (arguments.size() > 1)
						key = arguments[1];
					let_client_join_channel(arguments[0], client, key);
				}
			}
		}
		else if (command == "PART" && client.get_register_status() == true)
		{
			if (arguments.empty())
			{
				send_error_reply(client, "461", "PART :Not enough parameters");
				return ;
			}
			part_client_from_channel(client, arguments[0]);
		}
		else if (command == "KICK" && client.get_register_status() == true)
			handle_kick(client, line, arguments);
		else if (command == "INVITE" && client.get_register_status() == true)
			handle_invite(client, arguments);
		else if (command == "TOPIC" && client.get_register_status() == true)
			handle_topic(client, line, arguments);
		else if (command == "MODE" && client.get_register_status() == true)
			handle_mode(client, line, arguments);
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





///////////////////////////////////////////////////////////////////////////////
// Main Loop

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
					char	buffer[512];

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
							int disconnected_fd = fds[index].fd;
							cleanup_client_disconnect(disconnected_fd);
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

							int disconnected_fd = fds[index].fd;
							cleanup_client_disconnect(disconnected_fd);
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
