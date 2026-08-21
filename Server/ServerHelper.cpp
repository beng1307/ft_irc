#include "Server.hpp"
#include <sstream>
#include <iostream>
#include "../helpers/print.hpp"
#include "../helpers/Wire.hpp"

//Checks if the string is a positive number above 0
bool	Server::is_positive_number(const Wire &value)
{
	return (value.toInt() > 0 && value.toInt().toStr() == value);
}

//Checks if the nickname is valid: non-empty, contains only letters (a-z, A-Z), digits (0-9), and underscore (_)
bool	Server::is_valid_nickname(const Wire &nickname) { return  nickname.hasOnlyAlphaNum("_") ;}


//Creates a new filedescriptor and adds it to the fds.
//Events are the events to monitor and the reevents are
//the events that have occurred.
void	Server::add_fds(int fd, short events, short revents)
{
	pollfd poll_filedescriptor;

	poll_filedescriptor.fd = fd;
	poll_filedescriptor.events = events;
	poll_filedescriptor.revents = revents;

	get_fds().push_back(poll_filedescriptor);
}

//Checks if it's a legit command from the client.
bool	Server::is_command(const Wire &line)
{
	return (line == "PASS" || line == "USER" || line == "NICK" || line == "JOIN" 
		|| line == "PART" || line == "PRIVMSG" || line == "KICK"
		|| line == "INVITE" || line == "TOPIC" || line == "MODE" || line == "CAP"
		|| line == "PING" || line == "QUIT");
}

//A splitting function for the arguments.
Vector<Wire>	Server::split_arguments(const Wire &line)
{
	return line.strAfter(" ").splitBy(' ').filter(is_empty);
}

//Registers the client once the password, nickname, and username are valid
//and sends welcome message.
void	Server::try_register_client(Client &client)
{
	if (client.get_register_status())
		return ;
	if (!client.get_pass_ok())
		return ;
	if (client.get_nickname().empty() || client.get_username().empty())
		return ;

	client.set_register_status(true);
	print("Client ", client.get_nickname(), " registered successfully!");
	// welcome message
	send_status(client, "001", ":Welcome to ft_irc");
	send_status(client, "002", ":Your host is localhost");
	send_status(client, "003", ":This server was created today");
	send_status(client, "004", "localhost ft_irc 1.0 o o");
}