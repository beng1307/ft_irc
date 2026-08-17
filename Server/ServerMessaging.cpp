#include "Server.hpp"
#include <sys/socket.h>
#include <string>
#include <set>

//Sends a message into the channel
void	Server::send_message_to_channel(Client &sender, const std::string &channel_name, const std::string &message)
{
	ChannelMap::iterator it = get_channels().find(channel_name);
	if (it == get_channels().end())
	{
		send_error_reply(sender, "403", channel_name + " :No such channel");
		return ;
	}

	if (!it->second.has_member(sender.get_socket()))
	{
		send_error_reply(sender, "442", channel_name + " :You're not on that channel");
		return ;
	}

	std::set<int>	member_fds = it->second.get_member_fds();

	std::string	message_to_send = ":" + sender.get_nickname() + "!" + sender.get_username()
						+ "@localhost PRIVMSG " + channel_name + " :" + message + "\r\n";

	for (std::set<int>::const_iterator mit = member_fds.begin(); mit != member_fds.end(); ++mit)
	{
		if (*mit != sender.get_socket())
			send(*mit, message_to_send.c_str(), message_to_send.size(), 0);
	}
}

//Sends the error to a client
void	Server::send_error_reply(Client &client, const std::string &code, const std::string &message)
{
	std::string nick = client.get_nickname();

	if (nick.empty())
		nick = "*";

	std::string reply = ":localhost " + code + " " + nick + " " + message + "\r\n";
	send(client.get_socket(), reply.c_str(), reply.size(), 0);
}


//Sends a message to a client
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


void	Server::broadcast_to_channel(const Channel &channel, const std::string &message)
{
	std::set<int> member_fds = channel.get_member_fds();
	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send(*it, message.c_str(), message.size(), 0);
}

//Informs the members of a channel, that a new client joined.
void	Server::broadcast_join_to_channel(Client &joining_client, const std::string &channel_name)
{
	if (get_channels().find(channel_name) == get_channels().end())
	{
		send_error_reply(joining_client, "403", channel_name + " :No such channel");
		return ;
	}

	std::set<int>	member_fds = get_channels()[channel_name].get_member_fds();

	std::string join_message = ":" + joining_client.get_nickname() + "!"
    + joining_client.get_username() + "@localhost JOIN " + channel_name + "\r\n";

	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send(*it, join_message.c_str(), join_message.size(), 0);
}

// Informs the members of a channel that a member left.
void	Server::broadcast_part_to_channel(Client &parting_client, const std::string &channel_name,
		const std::string &reason)
{
	std::set<int> member_fds = get_channels()[channel_name].get_member_fds();
	std::string part_message = ":" + parting_client.get_nickname() + "!"
		+ parting_client.get_username() + "@localhost PART " + channel_name;

	if (!reason.empty())
		part_message += " :" + reason;
	part_message += "\r\n";
	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send(*it, part_message.c_str(), part_message.size(), 0);
}

//Sends a welcoming message to client
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

// Sends the RPL_NAMREPLY (353) and RPL_ENDOFNAMES (366) numeric responses to a client.
// Situation: Triggered when a client successfully joins a channel or queries channel names.
// What it does:
// 1. Constructs a space-separated list of nicknames currently in the channel.
// 2. Prefixes nicknames of channel operators with '@'.
// 3. Sends 353 RPL_NAMREPLY followed by 366 RPL_ENDOFNAMES back to the requesting client.
void	Server::send_channel_names_reply(Client &client, const std::string &channel_name)
{
	ChannelMap::iterator channel_it = get_channels().find(channel_name);
	if (channel_it == get_channels().end())
		return ;

	const Channel &channel = channel_it->second;
	std::string names;
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

	std::string nick = client.get_nickname().empty() ? "*" : client.get_nickname();
	std::string namreply = ":localhost 353 " + nick + " = " + channel_name + " :" + names + "\r\n";
	send(client.get_socket(), namreply.c_str(), namreply.size(), 0);

	std::string endofnames = ":localhost 366 " + nick + " " + channel_name + " :End of /NAMES list\r\n";
	send(client.get_socket(), endofnames.c_str(), endofnames.size(), 0);
}
