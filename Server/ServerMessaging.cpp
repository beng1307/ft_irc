#include "Server.hpp"
#include <sys/socket.h>
#include <string>
#include <set>


void	Server::send_message_to_channel(Client &sender, const std::string &channel_name, const std::string &message)
{
	if (get_channels().find(channel_name) == get_channels().end())
	{
		send_error_reply(sender, "403", channel_name + " :No such channel");
		return ;
	}

	std::set<int>	member_fds = get_channels()[channel_name].get_member_fds();

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