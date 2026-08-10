#include "Channel.hpp"
#include "../Client/Client.hpp"
#include <string>
#include <vector>
#include <algorithm>
#include <set>


///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Channel::Channel(): name(""), topic(""), member_fds(), operator_fds(), invited_fds(),
	invite_only(false), topic_restricted(false), key_enabled(false), channel_key(""),
	limit_enabled(false), user_limit(0)
{
	return ;
}

Channel::Channel(const std::string &name): name(name), topic(""), member_fds(), operator_fds(), invited_fds(),
	invite_only(false), topic_restricted(false), key_enabled(false), channel_key(""),
	limit_enabled(false), user_limit(0)
{
	return ;
}

Channel::Channel(const Channel &other): name(other.name), topic(other.topic),
	member_fds(other.member_fds), operator_fds(other.operator_fds), invited_fds(other.invited_fds),
	invite_only(other.invite_only), topic_restricted(other.topic_restricted),
	key_enabled(other.key_enabled), channel_key(other.channel_key),
	limit_enabled(other.limit_enabled), user_limit(other.user_limit)
{
	return ;
}

Channel	&Channel::operator=(const Channel &other)
{
	if (this != &other)
	{
		name = other.name;
		topic = other.topic;
		member_fds = other.member_fds;
		operator_fds = other.operator_fds;
		invited_fds = other.invited_fds;
		invite_only = other.invite_only;
		topic_restricted = other.topic_restricted;
		key_enabled = other.key_enabled;
		channel_key = other.channel_key;
		limit_enabled = other.limit_enabled;
		user_limit = other.user_limit;
	}

	return (*this);
}

Channel::~Channel()
{
	return ;
}


///////////////////////////////////////////////////////////////////////////////
// Setter, Getter & Helper

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

void	Channel::add_member(int client_fd)
{
	if (has_member(client_fd))
		return ;

	member_fds.insert(client_fd);
}

bool	Channel::has_member(int client_fd) const
{
	return (member_fds.find(client_fd) != member_fds.end());
}

//Erases member from the member/operater/invited fds.
void	Channel::remove_member(int client_fd)
{
	invited_fds.erase(client_fd);
	operator_fds.erase(client_fd);
	member_fds.erase(client_fd);
}

void	Channel::add_operator(int client_fd)
{
	if (!has_member(client_fd))
		return ;
	operator_fds.insert(client_fd);
}

bool	Channel::is_operator(int client_fd) const
{
	return (operator_fds.find(client_fd) != operator_fds.end());
}

void	Channel::add_invited(int client_fd)
{
	invited_fds.insert(client_fd);
}

bool	Channel::is_invited(int client_fd) const
{
	return (invited_fds.find(client_fd) != invited_fds.end());
}

void	Channel::set_invite_only(bool enabled)
{
	invite_only = enabled;
}

bool	Channel::is_invite_only() const
{
	return (invite_only);
}

void	Channel::set_topic_restricted(bool enabled)
{
	topic_restricted = enabled;
}

bool	Channel::is_topic_restricted() const
{
	return (topic_restricted);
}

void	Channel::set_key(const std::string &key)
{
	channel_key = key;
	key_enabled = true;
}

void	Channel::clear_key()
{
	channel_key.clear();
	key_enabled = false;
}

bool	Channel::has_key() const
{
	return (key_enabled);
}

std::string	Channel::get_key() const
{
	return (channel_key);
}

void	Channel::set_user_limit(size_t limit)
{
	user_limit = limit;
	limit_enabled = true;
}

void	Channel::clear_user_limit()
{
	user_limit = 0;
	limit_enabled = false;
}

bool	Channel::has_user_limit() const
{
	return (limit_enabled);
}

size_t	Channel::get_user_limit() const
{
	return (user_limit);
}

std::set<int>	Channel::get_member_fds() const
{
	return (member_fds);
}

