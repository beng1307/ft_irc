#include "Server.hpp"
#include <sys/socket.h>
#include <string>
#include <set>
#include "../helpers/Wire.hpp"

Wire	make_msg(const Client &client, const Wire &cmd, const Wire &target, const Wire &param)
{
	Wire msg(":", client.get_nickname(), "!", client.get_username(), "@localhost ", cmd, " ", target);
	if (!param.empty() || cmd == "TOPIC") // case TOPIC can use empty string to clear Topic
		msg += " :" + param;
	return msg;
}

ssize_t	send_string(int fd, const Wire &str)
{
	if (str.length() >= 2 && str.substr(str.length() - 2) == "\r\n")
		return send(fd, str.c_str(), str.size(), 0);
	Wire out = str + "\r\n";
	return send(fd, out.c_str(), out.size(), 0);
}

ssize_t	send_msg(int fd, const Client &client, const Wire &cmd, const Wire &target, const Wire &param)
{
	return send_string(fd, make_msg(client, cmd, target, param));
}

//Sends a status/reply to a client
void	Server::send_status(Client &client, const Wire &code, const Wire &message)
{
	send_string(client.get_socket(), Wire(":localhost ", code, " ", client.get_nickname().placeholder("*"), " ", message));
}


//Sends a message into the channel
void	Server::send_message_to_channel(Client &sender, const Wire &channel_name, const Wire &message)
{
	ChannelMap::iterator it = get_channels().find(channel_name);
	if (it == get_channels().end())
	{
		send_status(sender, "403", channel_name + " :No such channel");
		return ;
	}

	if (!it->second.has_member(sender.get_socket()))
	{
		send_status(sender, "442", channel_name + " :You're not on that channel");
		return ;
	}

	std::set<int>	member_fds = it->second.get_member_fds();

	Wire	message_to_send = make_msg(sender, "PRIVMSG", channel_name, message);

	for (std::set<int>::const_iterator mit = member_fds.begin(); mit != member_fds.end(); ++mit)
	{
		if (*mit != sender.get_socket())
			send_string(*mit, message_to_send);
	}
}




//Sends a message to a client
void	Server::send_message_to_user(Client &sender, const Wire &nickname, const Wire &message)
{
	Client *target = find_client_by_nickname(nickname);

	if (target == NULL)
	{
		send_status(sender, "401", nickname + " :No such nick/channel");
		return ;
	}

	send_msg(target->get_socket(), sender, "PRIVMSG", nickname, message);
}


void	Server::broadcast_to_channel(const Channel &channel, const Wire &message)
{
	std::set<int> member_fds = channel.get_member_fds();
	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send_string(*it, message);
}

//Informs the members of a channel, that a new client joined.
void	Server::broadcast_join_to_channel(Client &joining_client, const Wire &channel_name)
{
	if (get_channels().find(channel_name) == get_channels().end())
	{
		send_status(joining_client, "403", channel_name + " :No such channel");
		return ;
	}

	std::set<int>	member_fds = get_channels()[channel_name].get_member_fds();

	Wire join_message = make_msg(joining_client, "JOIN", channel_name);

	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send_string(*it, join_message);
}

// Informs the members of a channel that a member left.
void	Server::broadcast_part_to_channel(Client &parting_client, const Wire &channel_name,
		const Wire &reason)
{
	std::set<int> member_fds = get_channels()[channel_name].get_member_fds();
	Wire part_message = make_msg(parting_client, "PART", channel_name, reason);

	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send_string(*it, part_message);
}

// Sends the RPL_NAMREPLY (353) and RPL_ENDOFNAMES (366) numeric responses to a client.
// Situation: Triggered when a client successfully joins a channel or queries channel names.
// What it does:
// 1. Constructs a space-separated list of nicknames currently in the channel.
// 2. Prefixes nicknames of channel operators with '@'.
// 3. Sends 353 RPL_NAMREPLY followed by 366 RPL_ENDOFNAMES back to the requesting client.
void	Server::send_channel_names_reply(Client &client, const Wire &channel_name)
{
	ChannelMap::iterator channel_it = get_channels().find(channel_name);
	if (channel_it == get_channels().end())
		return ;

	const Channel &channel = channel_it->second;
	Wire names;
	std::set<int> member_fds = channel.get_member_fds();
	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
	{
		ClientMap::const_iterator client_it = get_clients().find(*it);
		if (client_it != get_clients().end())
		{
			if (!names.empty())
				names += " ";
			if (channel.is_operator(*it))
				names += "@";
			names += client_it->second.get_nickname();
		}
	}

	send_status(client, "353", "= " + channel_name + " :" + names);
	send_status(client, "366", channel_name + " :End of /NAMES list");
}
