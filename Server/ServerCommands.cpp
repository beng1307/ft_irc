#include "Server.hpp"
#include <string>
#include <vector>
#include <cstring>
#include <sys/socket.h>
#include <unistd.h>
#include <iostream>


//Joins the client to a channel after checking access restrictions.
void	Server::let_client_join_channel(const std::string &channel_name, Client &client, const std::string &key)
{
	int client_fd = client.get_socket();

	//If the channel doesn't exist yet, it gets created and the clients gets added as operator.
	if (get_channels().find(channel_name) == get_channels().end())
	{
		get_channels()[channel_name] = Channel(channel_name);
		std::cout << "Channel " << channel_name << " created!" << std::endl;
 
		get_channels()[channel_name].add_member(client_fd);
		get_channels()[channel_name].add_operator(client_fd);
		broadcast_join_to_channel(client, channel_name);
		std::cout << "Client joined channel " << channel_name << "!" << std::endl;
		return ;
	}

	Channel &channel = get_channels()[channel_name];

	//It gets checked if the client has the right to join.

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

	//Client gets added to the Channel, his invite gets reset
	//and all members in the channel get informed.
	channel.add_member(client_fd);
	channel.remove_invited(client_fd);
	broadcast_join_to_channel(client, channel.get_name());
	std::cout << "Client joined channel " << channel_name << "!" << std::endl;

}


//Parts the given client from the channel.
void	Server::part_client_from_channel(Client &client, const std::string &channel_name,
		const std::string &reason)
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

	broadcast_part_to_channel(client, channel_name, reason);
	it->second.remove_member_from_channel(client.get_socket());
	std::cout << "Client left channel " << it->second.get_name() << "!" << std::endl;
}

//Handles a password input.
//If a password is there, the client is not registered yet and the password
//is correct, the password gets set.
//If nick, user and pass are set, he gets registered.
void	Server::handle_pass_command(Client &client, const std::vector<std::string> &arguments)
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

//Handles the new username.
//If nick, user and pass are set, he gets registered.
void	Server::handle_user_command(Client &client, const std::vector<std::string> &arguments)
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

//Handles the new nickname.
//First it checks if the nickname is already in use.
//If not and nick, user and pass are set, he gets registered.
void	Server::handle_nick_command(Client &client, const std::vector<std::string> &arguments)
{
	if (arguments.empty())
	{
		send_error_reply(client, "431", ":No nickname given");
		return ;
	}
	// TODO: maybe check if the nickname is valid.
	Client *existing_client = find_client_by_nickname(arguments[0]);
	if (existing_client != NULL
		&& existing_client->get_socket() != client.get_socket())
	{
		send_error_reply(client, "433", arguments[0] + " :Nickname is already in use");
		return ;
	}

	//Updates the nickname and informs the client
	std::string old_nick = client.get_nickname();
	std::string new_nick = arguments[0];

	std::string nick_message = ":" + old_nick + "!"
    	+ client.get_username() + "@localhost NICK :" + new_nick + "\r\n";

	send(client.get_socket(), nick_message.c_str(), nick_message.size(), 0);	
	client.set_nickname(new_nick);
	try_register_client(client);
}


//Handles the join command.
//If there is a key, it will gets set. And used for joining.
void	Server::handle_join_command(Client &client, const std::vector<std::string> &arguments)
{
	if (arguments.empty())
	{
		send_error_reply(client, "461", "JOIN :Not enough parameters");
		return ;
	}

	std::string key;
	if (arguments.size() > 1)
		key = arguments[1];
	let_client_join_channel(arguments[0], client, key);
}

//Parts the given client from the channel.
void	Server::handle_part_command(Client &client, const std::string &line,
		const std::vector<std::string> &arguments)
{
	if (arguments.empty())
	{
		send_error_reply(client, "461", "PART :Not enough parameters");
		return ;
	}
	std::string reason;
	size_t reason_start = line.find(" :");
	if (reason_start != std::string::npos)
		reason = line.substr(reason_start + 2);
	part_client_from_channel(client, arguments[0], reason);
}

//When the client asks about extra capabilities of the server on connect, it gives a response that it doesn't have them.
void	Server::handle_cap_command(Client &client, const std::vector<std::string> &arguments)
{
	if (arguments.size() > 0)
	{
		if (arguments[0] == "LS")
		{
			std::string cap_response = ":localhost CAP * LS :\r\n";
			send(client.get_socket(), cap_response.c_str(), cap_response.size(), 0);
		}
		else if (arguments[0] == "END") {}
	}
}

void	Server::handle_privmsg_command(Client &client, const std::string &line,
		const std::vector<std::string> &arguments)
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
		message = line.substr(position + 2);
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

void	Server::handle_quit_command(Client &client, const std::string &line,
		const std::vector<std::string> &arguments)
{
	std::string reason = "Leaving server";
	size_t reason_start = line.find(" :");
	if (reason_start != std::string::npos)
		reason = line.substr(reason_start + 2);
	else if (!arguments.empty())
		reason = arguments[0];

	std::string nick = client.get_nickname();
	std::string user = client.get_username();
	std::string prefix = ":" + nick + "!" + user + "@localhost";
	std::string quit_message = prefix + " QUIT :" + reason + "\r\n";

	std::set<int> recipient_fds;
	for (ChannelMap::const_iterator cit = get_channels().begin(); cit != get_channels().end(); ++cit)
	{
		if (cit->second.has_member(client.get_socket()))
		{
			const std::set<int> &members = cit->second.get_member_fds();
			for (std::set<int>::const_iterator mit = members.begin(); mit != members.end(); ++mit)
			{
				if (*mit != client.get_socket())
					recipient_fds.insert(*mit);
			}
		}
	}

	for (std::set<int>::const_iterator rit = recipient_fds.begin(); rit != recipient_fds.end(); ++rit)
	{
		send(*rit, quit_message.c_str(), quit_message.size(), 0);
	}

	std::string bye = "ERROR :Closing connection\r\n";
	send(client.get_socket(), bye.c_str(), bye.size(), 0);

	cleanup_client_disconnect(client.get_socket());
	close(client.get_socket());
	client.get_buffer().clear();
}

//Checks which command it is and uses the right function for it.
void	Server::dispatch_command(Client &client, const std::string &command,
		const std::string &line, const std::vector<std::string> &arguments)
{
	// TODO: Maybe put the register check in the functions and send a errormessage.
	if (command == "PASS")
		handle_pass_command(client, arguments);
	else if (command == "USER")
		handle_user_command(client, arguments);
	else if (command == "NICK")
		handle_nick_command(client, arguments);
	else if (command == "JOIN" && client.get_register_status() == true)
		handle_join_command(client, arguments);
	else if (command == "PART" && client.get_register_status() == true)
		handle_part_command(client, line, arguments);
	else if (command == "KICK" && client.get_register_status() == true)
		handle_kick(client, line, arguments);
	else if (command == "INVITE" && client.get_register_status() == true)
		handle_invite(client, arguments);
	else if (command == "TOPIC" && client.get_register_status() == true)
		handle_topic(client, line, arguments);
	else if (command == "MODE" && client.get_register_status() == true)
		handle_mode(client, line, arguments);
	else if (command == "CAP")
		handle_cap_command(client, arguments);
	else if (command == "PRIVMSG" && client.get_register_status() == true)
		handle_privmsg_command(client, line, arguments);
	else if (command == "PING")
	{
		std::string token = arguments.empty() ? "localhost" : arguments[0];
		std::string pong = ":localhost PONG localhost :" + token + "\r\n";
		send(client.get_socket(), pong.c_str(), pong.size(), 0);
	}
	else if (command == "QUIT")
		handle_quit_command(client, line, arguments);
}


//Handles the message from client.
void Server::handle_line(Client &client, const size_t &position)
{
	//Saves the message in line and removes the message form the client buffer.
	std::string	line;

	line = client.get_buffer().substr(0, position);
	// erase delimiter before checking if empty
	client.get_buffer().erase(0, position + 2);
	if (line.empty())
		return ;

	//It gets the first word of the message, because it's a potential command.
	//It also makes it uppercase for checks. Because the commands are case insensetive.
	std::string command;
	size_t 		space = line.find(' ');

	if (space == std::string::npos)
		command = line;
	else
		command = line.substr(0, space);

	std::transform(command.begin(), command.end(), command.begin(), ::toupper);
	
	//Checks if it's a command.
	//If it is, it extracts the arguments and handles the command.
	//Else it sends a error reply.
	if (is_command(command))
	{
		std::vector<std::string>	arguments = split_arguments(line);
		dispatch_command(client, command, line, arguments);
	}
	else
		send_error_reply(client, "421", "Unknown command.");
}
