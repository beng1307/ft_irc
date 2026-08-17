#include "Server.hpp"
#include <string>
#include <vector>
#include <cstring>
#include <sys/socket.h>
#include <unistd.h>
#include <iostream>
#include "../helpers/print.hpp"
#include "../helpers/Wire.hpp"



//Joins the client to a channel after checking access restrictions.
void	Server::let_client_join_channel(const Wire &channel_name, Client &client, const Wire &key)
{
	int client_fd = client.get_socket();

	//If the channel doesn't exist yet, it gets created and the clients gets added as operator.
	if (get_channels().find(channel_name) == get_channels().end())
	{
		get_channels()[channel_name] = Channel(channel_name);
		print("Channel ", channel_name, " created!");
 
		get_channels()[channel_name].add_member(client_fd);
		get_channels()[channel_name].add_operator(client_fd);
		broadcast_join_to_channel(client, channel_name);
		print("Client joined channel ", channel_name, "!");
	}
	else
	{
		Channel &channel = get_channels()[channel_name];

		//It gets checked if the client has the right to join.

		if (channel.has_member(client_fd))
		{
			print("Client is already in channel ", channel_name, "!");
			return ;
		}

		if (channel.is_invite_only() && !channel.is_invited(client_fd)
			&& !channel.is_operator(client_fd))
		{
			send_status(client, "473", channel_name + " :Cannot join channel (+i)");
			return ;
		}

		if (channel.has_key() && channel.get_key() != key)
		{
			send_status(client, "475", channel_name + " :Cannot join channel (+k)");
			return ;
		}

		if (channel.has_user_limit()
			&& channel.get_member_fds().size() >= channel.get_user_limit())
		{
			send_status(client, "471", channel_name + " :Cannot join channel (+l)");
			return ;
		}

		//Client gets added to the Channel, his invite gets reset
		//and all members in the channel get informed.
		channel.add_member(client_fd);
		channel.remove_invited(client_fd);
		broadcast_join_to_channel(client, channel.get_name());
		print("Client joined channel ", channel_name, "!");
	}

	// Sends mandatory IRC numeric replies 353 RPL_NAMREPLY (member list with '@' for ops)
	// and 366 RPL_ENDOFNAMES back to the client upon joining the channel.
	send_channel_names_reply(client, channel_name);
}


//Parts the given client from the channel.
void	Server::part_client_from_channel(Client &client, const Wire &channel_name,
		const Wire &reason)
{
	ChannelMap::iterator it = get_channels().find(channel_name);
	if (it == get_channels().end())
	{
		send_status(client, "403", channel_name + " :No such channel");
		return ;
	}

	if (!it->second.has_member(client.get_socket()))
	{
		send_status(client, "442", channel_name + " :You're not on that channel");
		return ;
	}

	broadcast_part_to_channel(client, channel_name, reason);
	it->second.remove_member_from_channel(client.get_socket());
	if (it->second.get_member_fds().empty())
		get_channels().erase(it);
	print("Client left channel ", channel_name, "!");
}

//Handles a password input.
//If a password is there, the client is not registered yet and the password
//is correct, the password gets set.
//If nick, user and pass are set, he gets registered.
void	Server::handle_pass_command(Client &client, const std::vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "461", "PASS :Not enough parameters");
		return ;
	}
	if (client.get_register_status())
	{
		send_status(client, "462", ":You may not reregister");
		return ;
	}
	if (arguments[0] != get_password())
	{
		client.set_pass_ok(false);
		send_status(client, "464", ":Password incorrect");
		return ;
	}
	client.set_password(arguments[0]);
	client.set_pass_ok(true);
	try_register_client(client);
}

//Handles the new username.
//If nick, user and pass are set, he gets registered.
void	Server::handle_user_command(Client &client, const std::vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "461", "USER :Not enough parameters");
		return ;
	}
	if (client.get_register_status())
	{
		send_status(client, "462", ":You may not reregister");
		return ;
	}
	client.set_username(arguments[0]);
	try_register_client(client);
}

//Handles the new nickname.
//First it checks if the nickname is already in use.
//If not and nick, user and pass are set, he gets registered.
void	Server::handle_nick_command(Client &client, const std::vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "431", ":No nickname given");
		return ;
	}
	if (!is_valid_nickname(arguments[0]))
	{
		send_status(client, "432", arguments[0] + " :Erroneous nickname");
		return ;
	}
	Client *existing_client = find_client_by_nickname(arguments[0]);
	if (existing_client != NULL
		&& existing_client->get_socket() != client.get_socket()
		&& (existing_client->get_register_status() || existing_client->get_pass_ok()))
	{
		send_status(client, "433", arguments[0] + " :Nickname is already in use");
		return ;
	}

	//Updates the nickname and informs the client
	Wire old_nick = client.get_nickname();
	Wire new_nick = arguments[0];

	if (client.get_register_status())
	{
		Wire nick_message(":", old_nick, "!", client.get_username(), "@localhost NICK :", new_nick);

		std::set<int> recipient_fds;
		recipient_fds.insert(client.get_socket());
		for (ChannelMap::const_iterator cit = get_channels().begin(); cit != get_channels().end(); ++cit)
		{
			if (cit->second.has_member(client.get_socket()))
			{
				const std::set<int> &members = cit->second.get_member_fds();
				for (std::set<int>::const_iterator mit = members.begin(); mit != members.end(); ++mit)
					recipient_fds.insert(*mit);
			}
		}

		for (std::set<int>::const_iterator rit = recipient_fds.begin(); rit != recipient_fds.end(); ++rit)
			send_string(*rit, nick_message);
	}
	client.set_nickname(new_nick);
	try_register_client(client);
}


//Handles the join command.
//If there is a key, it will gets set. And used for joining.
void	Server::handle_join_command(Client &client, const std::vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "461", "JOIN :Not enough parameters");
		return ;
	}

	const Wire &chan = arguments[0];
	if (chan.empty() || (chan[0] != '#' && chan[0] != '&'))
	{
		send_status(client, "403", chan + " :No such channel");
		return ;
	}

	Wire key;
	if (arguments.size() > 1)
		key = arguments[1];
	let_client_join_channel(chan, client, key);
}

//Parts the given client from the channel.
void	Server::handle_part_command(Client &client, const Wire &line,
		const std::vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "461", "PART :Not enough parameters");
		return ;
	}
	Wire reason;
	if (line.contains(" :"))
		reason = line.strAfter(" :");
	part_client_from_channel(client, arguments[0], reason);
}

//When the client asks about extra capabilities of the server on connect, it gives a response that it doesn't have them.
void	Server::handle_cap_command(Client &client, const std::vector<Wire> &arguments)
{
	if (arguments.size() > 0)
	{
		if (arguments[0] == "LS")
		{
			Wire cap_response = ":localhost CAP * LS :";
			send_string(client.get_socket(), cap_response);
		}
		else if (arguments[0] == "END") {}
	}
}

void	Server::handle_privmsg_command(Client &client, const Wire &line,
		const std::vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "411", ":No recipient given (PRIVMSG)");
		return ;
	}

	Wire	message;
	Wire	target = arguments[0];

	if (line.contains(" :"))
		message = line.strAfter(" :");
	else if (arguments.size() > 1)
		message = arguments[1];

	if (message.empty())
	{
		send_status(client, "412", ":No text to send");
		return ;
	}

	if (!target.empty() && target[0] == '#')
		send_message_to_channel(client, target, message);
	else
		send_message_to_user(client, target, message);
}

void	Server::handle_quit_command(Client &client, const Wire &line,
		const std::vector<Wire> &arguments)
{
	Wire reason = "Leaving server";
	if (line.contains(" :"))
		reason = line.strAfter(" :");
	else if (!arguments.empty())
		reason = arguments[0];

	Wire nick = client.get_nickname();
	Wire user = client.get_username();
	Wire quit_message(":", nick, "!", user, "@localhost QUIT :", reason);

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
		send_string(*rit, quit_message);
	}

	int client_fd = client.get_socket();
	Wire bye = "ERROR :Closing connection";
	send_string(client_fd, bye);

	disconnect_client(client_fd);
}

void	Server::handle_ping_command(Client &client, const std::vector<Wire> &arguments)
{
	Wire token = arguments.empty() ? "localhost" : arguments[0];
	if (!token.empty() && token[0] == ':')
		token = token.substr(1);
	Wire pong(":localhost PONG localhost :", token);
	send_string(client.get_socket(), pong);
}

//Checks which command it is and uses the right function for it.
void	Server::dispatch_command(Client &client, const Wire &command,
		const Wire &line, const std::vector<Wire> &arguments)
{
	if (command == "PASS")
		handle_pass_command(client, arguments);
	else if (command == "USER")
		handle_user_command(client, arguments);
	else if (command == "NICK")
		handle_nick_command(client, arguments);
	else if (command == "CAP")
		handle_cap_command(client, arguments);
	else if (command == "PING")
		handle_ping_command(client, arguments);
	else if (command == "QUIT")
		handle_quit_command(client, line, arguments);
	else if (!client.get_register_status())
		send_status(client, "451", ":You have not registered");
	else if (command == "JOIN")
		handle_join_command(client, arguments);
	else if (command == "PART")
		handle_part_command(client, line, arguments);
	else if (command == "KICK")
		handle_kick(client, line, arguments);
	else if (command == "INVITE")
		handle_invite(client, arguments);
	else if (command == "TOPIC")
		handle_topic(client, line, arguments);
	else if (command == "MODE")
		handle_mode(client, line, arguments);
	else if (command == "PRIVMSG")
		handle_privmsg_command(client, line, arguments);
}


// Handles the message from client.
// Design Decision:
// 1. Bare \n without \r: Delimiting strictly on \r\n (standard IRC RFC 1459/2812). Bare \n is not supported as delimiter.
// 2. Leading whitespace: IRC grammar BNF specifies command begins immediately without leading spaces. Leading spaces cause the command token to be invalid/empty and yield ERR_UNKNOWNCOMMAND (421).
// 3. Empty lines (\r\n\r\n): Empty lines are completely ignored per RFC 2812 §2.3 and return without sending any response.
void Server::handle_line(Client &client, const size_t &position)
{
	// Saves the message in line and removes the message from the client buffer.
	Wire	line;

	line = client.get_buffer().substr(0, position);
	// erase delimiter before checking if empty
	client.get_buffer().erase(0, position + 2);
	if (line.empty())
		return ;

	// It gets the first word of the message and makes it uppercase for checks.
	Wire	command = line.splitBy(' ')[0].toUpper();
	
	// Checks if it's a command.
	// If it is, it extracts the arguments and handles the command.
	// Else it sends a error reply.
	if (is_command(command))
	{
		std::vector<Wire>	arguments = split_arguments(line);
		dispatch_command(client, command, line, arguments);
	}
	else
		send_status(client, "421", "Unknown command.");
}
