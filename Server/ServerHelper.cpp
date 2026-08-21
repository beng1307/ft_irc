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


#include <cstring>

// Adds a file descriptor to the epoll interest list.
// - get_epoll_fd(): The epoll instance file descriptor managing monitored events.
// - EPOLL_CTL_ADD: Operation flag instructing epoll to register the target fd.
// - fd: The target socket file descriptor to monitor.
// - &ev: Pointer to the epoll_event struct defining events to listen for (e.g. EPOLLIN) and associated data.
void	Server::add_epoll_fd(Fd fd, uint32_t events)
{
	if (!fd || !get_epoll_fd())
		return ;
	struct epoll_event ev;
	std::memset(&ev, 0, sizeof(ev));
	ev.events = events;
	ev.data.fd = fd;
	// Registers the file descriptor with epoll using the specified event mask.
	if (epoll_ctl(get_epoll_fd(), EPOLL_CTL_ADD, fd, &ev) == -1)
	{
		printErr("Error: epoll_ctl ADD failed!");
	}
}

// Removes a file descriptor from the epoll interest list.
// - get_epoll_fd(): The epoll instance file descriptor.
// - EPOLL_CTL_DEL: Operation flag instructing epoll to deregister/remove the target fd.
// - fd: The socket file descriptor to remove.
// - NULL: Ignored for DEL operations in Linux >= 2.6.9.
void	Server::remove_epoll_fd(Fd fd)
{
	if (get_epoll_fd() && fd)
	{
		epoll_ctl(get_epoll_fd(), EPOLL_CTL_DEL, fd, NULL);
	}
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