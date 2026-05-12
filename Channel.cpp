#include "Channel.hpp"
#include "Client.hpp"
#include <string>
#include <vector>
#include <algorithm>


///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Channel::Channel(): name(""), topic(""), members()
{
	return ;
}

Channel::Channel(const std::string &name): name(name), topic(""), members()
{
	return ;
}

Channel::Channel(const Channel &other): name(other.name), topic(other.topic), members(other.members)
{
	return ;
}

Channel	&Channel::operator=(const Channel &other)
{
	if (this != &other)
	{
		name = other.name;
		topic = other.topic;
		members = other.members;
	}

	return (*this);
}

Channel::~Channel()
{
	return ;
}

///////////////////////////////////////////////////////////////////////////////
// Methods

// void	Channel::kick()
// {
// }

// void	Channel::invite()
// {
// }

// void	Channel::topic()
// {
// }

// void	Channel::mode()
// {
// }

///////////////////////////////////////////////////////////////////////////////
// Setter & Getter

void	Channel::set_name(const std::string &name)
{
	this->name = name;
}

std::string	Channel::get_name() const
{
	return (name);
}

void	Channel::set_topic(const std::string &topic)
{
	this->topic = topic;
}

std::string	Channel::get_topic() const
{
	return (topic);
}

void	Channel::add_member(const Client &client)
{
	if (has_member(client))
		return ;

	members.push_back(client);
}

bool	Channel::has_member(const Client &client) const
{
	for (std::vector<Client>::const_iterator it = members.begin(); it != members.end(); ++it)
	{
		if (it->get_socket() == client.get_socket())
			return (true);
	}

	return (false);
}

void	Channel::remove_member(const Client &client)
{
	for (std::vector<Client>::iterator it = members.begin(); it != members.end(); ++it)
	{
		if (it->get_socket() == client.get_socket())
		{
			members.erase(it);
			return ;
		}
	}
}

std::vector<Client>	Channel::get_members() const
{
	return (members);
}

