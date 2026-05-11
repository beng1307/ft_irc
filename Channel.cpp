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
	members.push_back(client);
}

void	Channel::remove_member(const Client &client)
{
	members.erase(std::remove(members.begin(), members.end(), client), members.end()); //Check this function if it works correctly
}

std::vector<Client>	Channel::get_members() const
{
	return (members);
}

