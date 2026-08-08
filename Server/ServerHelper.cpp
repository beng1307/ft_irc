#include "Server.hpp"
#include <sstream>
#include <iostream>

//Returns a string converted from size_t
std::string	Server::to_string_size_t(size_t value)
{
	std::ostringstream oss;
	oss << value;
	return (oss.str());
}

//Checks if the string is a positive number above 0
bool	Server::is_positive_number(const std::string &value)
{
	if (value.empty())
		return (false);
	for (size_t i = 0; i < value.size(); ++i)
	{
		if (!std::isdigit(static_cast<unsigned char>(value[i])))
			return (false);
	}
	if (value == "0")
		return (false);
	return (true);
}


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
bool	Server::is_command(const std::string &line)
{
	return (line == "PASS" || line == "USER" || line == "NICK" || line == "JOIN" 
		|| line == "PART" || line == "PRIVMSG" || line == "KICK"
		|| line == "INVITE" || line == "TOPIC" || line == "MODE" || line == "CAP");
}

//A splitting function for the arguments.
std::vector<std::string>	Server::split_arguments(const std::string &line)
{
	std::vector<std::string>	arguments;
	size_t						start = line.find(" ");
	
	if (start == std::string::npos)
		return (arguments);

	while (start < line.length() && line[start] == ' ')
		start++;	

	while (start < line.length())
	{
		size_t	end = line.find(" ", start);
		if (end == std::string::npos)
		{
			arguments.push_back(line.substr(start));
			break ;			
		}
		
		arguments.push_back(line.substr(start, end - start));
		start = end + 1;
		while (start < line.length() && line[start] == ' ')
			start++;
	}
	
	return (arguments);
}

//It goes through the clients and if he gets found per name, he gets returned.
Client	*Server::find_client_by_nickname(const std::string &nickname)
{
	for (ClientMap::iterator it = get_clients().begin(); it != get_clients().end(); ++it)
	{
		if (it->second.get_nickname() == nickname)
			return (&it->second);
	}
	return (NULL);
}

//Removes the disconnected client from all channels and deletes any channels
//that have no members left.
void	Server::cleanup_client_disconnect(int disconnected_fd)
{
	for (ChannelMap::iterator it = get_channels().begin(); it != get_channels().end();)
	{
		it->second.remove_member(disconnected_fd);
		if (it->second.get_member_fds().empty())
			get_channels().erase(it++);
		else
			++it;
	}
}

//Registers the client once the password, nickname, and username are valid
//and sends welcome message.
void	Server::try_register_client(Client &client)
{
	//TODO: Check if the behaviour is correct and if Error messages need to be added
	if (client.get_register_status())
		return ;
	if (!client.get_pass_ok())
		return ;
	if (client.get_nickname().empty() || client.get_username().empty())
		return ;

	client.set_register_status(true);
	std::cout << "Client " << client.get_nickname() << " registered successfully!" << std::endl;
	send_welcome_message(client);
}