#include "Server.hpp"
#include <string>
#include <vector>
#include <cstring>
#include <algorithm>
#include <sys/socket.h>
#include <unistd.h>
#include "../helpers/print.hpp"
#include "../helpers/Wire.hpp"



//Joins the client to a channel after checking access restrictions.
void	Server::let_client_join_channel(const Wire &channel_name, Client &client, const Wire &key)
{
	int client_fd = client.get_socket();
	Channel &channel = get_channel(channel_name);
	if (!channel)
	{
		Channel &new_channel = create_new_channel(channel_name);
		new_channel.add_member(client_fd);
		new_channel.add_operator(client_fd);
		new_channel.broadcast(client, "JOIN");
		print("Client joined channel ", channel_name, "!");
		print("Channel ", channel_name, " created!");
	}
	else
	{
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
		channel.broadcast(client, "JOIN");
		print("Client joined channel ", channel_name, "!");
	}
	
	send_channel_topic_reply(client, channel_name);
	send_channel_names_reply(client, channel_name);
}


//Parts the given client from the channel.
void	Server::part_client_from_channel(Client &client, const Wire &channel_name,
		const Wire &reason)
{
	Channel &channel = get_channel(channel_name);
	if (!channel)
	{
		send_status(client, "403", channel_name + " :No such channel");
		return ;
	}

	if (!channel.has_member(client.get_socket()))
	{
		send_status(client, "442", channel_name + " :You're not on that channel");
		return ;
	}

	channel.broadcast(client, "PART", reason);
	channel.remove_client_from_channel(client.get_socket());
	print("Client left channel ", channel_name, "!");
}

//Handles a password input.
//If a password is there, the client is not registered yet and the password
//is correct, the password gets set.
//If nick, user and pass are set, he gets registered.
void	Server::handle_pass_command(Client &client, const Vector<Wire> &arguments)
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
void	Server::handle_user_command(Client &client, const Vector<Wire> &arguments)
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
	if (!is_valid_nickname(arguments[0]))
	{
		send_status(client, "432", arguments[0] + " :Erroneous nickname");
		return ;
	}
	if (arguments.size() < 4)
	{
		send_status(client, "461", "USER :Not enough parameters");
		return ;
	}
	client.set_username(arguments[0]);
	try_register_client(client);
}

//Handles the new nickname.
//First it checks if the nickname is already in use.
//If not and nick, user and pass are set, he gets registered.
void	Server::handle_nick_command(Client &client, const Vector<Wire> &arguments)
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
	if (is_nickname_in_use(arguments[0], client.get_socket()))
	{
		send_status(client, "433", arguments[0] + " :Nickname is already in use");
		return ;
	}

	//Updates the nickname and informs the client
	Wire new_nick = arguments[0];

	if (client.get_register_status())
	{
		// we do it like this because we want to avoid sending the same message 
		// multiple times to a client because they share multiple channels.
		get_client_audience(client.get_socket())
			.add(client.get_socket())
			.forEach(send_string_fn, make_msg(client, "NICK", ":" + new_nick), this);
	}
	client.set_nickname(new_nick);
	try_register_client(client);
}

//Handles the join command.
//If there is a key, it will gets set. And used for joining.
void	Server::handle_join_command(Client &client, const Vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "461", "JOIN :Not enough parameters");
		return ;
	}

	const Wire &chan = arguments[0];
	if (!is_valid_channel_name(chan))
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
void	Server::handle_part_command(Client &client, const Vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "461", "PART :Not enough parameters");
		return ;
	}
	Wire reason;
	if (arguments.size() > 1)
		reason = arguments[1];
	part_client_from_channel(client, arguments[0], reason);
}

//When the client asks about extra capabilities of the server on connect, it gives a response that it doesn't have them.
void	Server::handle_cap_command(Client &client, const Vector<Wire> &arguments)
{
	if (arguments.size() > 0)
	{
		if (arguments[0].toUpper() == "LS")
		{
			Wire cap_response = ":localhost CAP * LS :";
			client.send(cap_response);
		}
		else if (arguments[0].toUpper() == "REQ")
		{
			Wire requested_caps = arguments.size() > 1 ? arguments[1] : Wire();
			Wire cap_response(":localhost CAP * NAK :", requested_caps);
			client.send(cap_response);
		}
		else if (arguments[0].toUpper() == "END") {}
	}
}

void	Server::handle_privmsg_command(Client &client, const Vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "411", ":No recipient given (PRIVMSG)");
		return ;
	}

	Wire	message;
	Wire	channel_or_user_name = arguments[0];

	if (arguments.size() > 1)
		message = arguments[1];

	if (arguments.size() < 2)
	{
		send_status(client, "412", ":No text to send");
		return ;
	}

	if (!channel_or_user_name.empty() && channel_or_user_name[0] == '#')
		send_message_to_channel(client, channel_or_user_name, message);
	else
		send_message_to_user(client, channel_or_user_name, message);
}

void	Server::handle_quit_command(Client &client, const Vector<Wire> &arguments)
{
	Wire reason = "Leaving server";
	if (!arguments.empty())
		reason = arguments[0];

	get_client_audience(client.get_socket())
		.forEach(send_string_fn, make_msg(client, "QUIT", ":" + reason), this);

	Wire bye = "ERROR :Closing connection";
	// Defer the actual close until output buffer drains.
	client.should_disconnect(true);
	client.send(bye);
}

void	Server::handle_ping_command(Client &client, const Vector<Wire> &arguments)
{
	Wire token = arguments.empty() ? "localhost" : arguments[0];
	if (!token.empty() && token[0] == ':')
		token = token.substr(1);
	Wire pong(":localhost PONG localhost :", token);
	client.send(pong);
}

//Checks which command it is and uses the right function for it.
void	Server::dispatch_command(Client &client, const Wire &command,
		const Vector<Wire> &arguments)
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
		handle_quit_command(client, arguments);
	else if (!client.get_register_status())
		send_status(client, "451", ":You have not registered");
	else if (command == "JOIN")
		handle_join_command(client, arguments);
	else if (command == "PART")
		handle_part_command(client, arguments);
	else if (command == "KICK")
		handle_kick(client, arguments);
	else if (command == "INVITE")
		handle_invite(client, arguments);
	else if (command == "TOPIC")
		handle_topic(client, arguments);
	else if (command == "MODE")
		handle_mode(client, arguments);
	else if (command == "PRIVMSG")
		handle_privmsg_command(client, arguments);
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
	line.erase(std::remove(line.begin(), line.end(), '\r'), line.end());
	if (line.empty())
		return ;

	// It gets the first word of the message and makes it uppercase for checks.
	Wire	command = line.splitBy(' ')[0].toUpper();
	
	// Checks if it's a command.
	// If it is, it extracts the arguments and handles the command.
	// Else it sends a error reply.
	if (is_command(command))
	{
		Vector<Wire>	arguments = split_arguments(line);
		dispatch_command(client, command, arguments);
	}
	else
		send_status(client, "421", "Unknown command.");
}
