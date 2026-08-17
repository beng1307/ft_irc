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
