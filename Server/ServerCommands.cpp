#include "Server.hpp"
#include <string>
#include <vector>
#include <cstring>
#include <sys/socket.h>
#include <iostream>

void	Server::let_client_join_channel(const std::string &channel_name, Client &client, const std::string &key)
{
	int client_fd = client.get_socket();

	// Checks if the channel already exists, if not it gets created and a client gets added
	if (get_channels().find(channel_name) == get_channels().end())
	{
		get_channels()[channel_name] = Channel(channel_name);
		std::cout << "Channel " << channel_name << " created!" << std::endl;
 
		get_channels()[channel_name].add_member(client_fd); // Check if its the correct client that gets added
		get_channels()[channel_name].add_operator(client_fd);
		std::cout << "Client joined channel " << channel_name << "!" << std::endl;
		return ;
	}

	Channel &channel = get_channels()[channel_name];

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
	ChannelMap::iterator it = get_channels().find(channel_name);
	if (it == get_channels().end())
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
			if (arguments[0] != get_password())
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
