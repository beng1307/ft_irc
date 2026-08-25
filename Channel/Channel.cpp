#include "Channel.hpp"
#include "../Client/Client.hpp"
#include "../Server/Server.hpp"
#include "../helpers/Wire.hpp"



///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Channel::Channel(): server(NULL), name(""), topic(""), member_fds(), operator_fds(), invited_fds(),
	invite_only(false), topic_restricted(false), key_enabled(false), channel_key(""),
	limit_enabled(false), user_limit(0)
{
	member_fds.ok();
	operator_fds.ok();
	invited_fds.ok();
	_ok = false;
	return ;
}

Channel::Channel(const Wire &name, Server *server): server(server), name(name), topic(""), member_fds(), operator_fds(), invited_fds(),
	invite_only(false), topic_restricted(false), key_enabled(false), channel_key(""),
	limit_enabled(false), user_limit(0)
{
	member_fds.ok();
	operator_fds.ok();
	invited_fds.ok();
	_ok = true;
	return ;
}

Channel::Channel(const Channel &other): server(other.server), name(other.name), topic(other.topic),
	member_fds(other.member_fds), operator_fds(other.operator_fds), invited_fds(other.invited_fds),
	invite_only(other.invite_only), topic_restricted(other.topic_restricted),
	key_enabled(other.key_enabled), channel_key(other.channel_key),
	limit_enabled(other.limit_enabled), user_limit(other.user_limit)
{
	_ok = other._ok;
	return ;
}

Channel	&Channel::operator=(const Channel &other)
{
	if (this != &other)
	{
		server = other.server;
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
		_ok = other._ok;
	}

	return (*this);
}

Channel::~Channel()
{
	return ;
}


///////////////////////////////////////////////////////////////////////////////
// Setter, Getter & Helper

void	Channel::set_server(Server *server)
{
	this->server = server;
}

Server	*Channel::get_server() const
{
	return (server);
}

void	Channel::set_name(const Wire &name)
{
	this->name = name;
}

Wire	Channel::get_name() const
{
	return (name);
}

void	Channel::set_topic(const Wire &topic)
{
	this->topic = topic;
}

Wire	Channel::get_topic() const
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
	return (member_fds.find(client_fd));
}

//Erases member from the member/operater/invited fds.
void	Channel::remove_client_from_channel(int client_fd)
{
	remove_invited(client_fd);
	remove_member(client_fd);
	if (empty() && server)
		server->remove_channel(name);
}

bool	Channel::remove_operator(int client_fd)
{
	if (!is_operator(client_fd))
		return (false);
	operator_fds.erase(client_fd);
	return (true);
}

void	Channel::remove_invited(int client_fd)
{
	invited_fds.erase(client_fd);
}

void	Channel::remove_member(int client_fd)
{
	member_fds.erase(client_fd);
	remove_operator(client_fd);
}

void	Channel::promote_first_member_if_no_operators()
{
	if (operator_fds.empty() && !member_fds.empty())
		add_operator(*member_fds.begin());
}

bool	Channel::add_operator(int client_fd)
{
	if (!has_member(client_fd) || is_operator(client_fd))
		return (false);
	operator_fds.insert(client_fd);
	return (true);
}

bool	Channel::is_operator(int client_fd) const
{
	return (operator_fds.find(client_fd));
}

void	Channel::add_invited(int client_fd)
{
	invited_fds.insert(client_fd);
}

bool	Channel::is_invited(int client_fd) const
{
	return (invited_fds.find(client_fd));
}

bool	Channel::set_invite_only(bool enabled)
{
	if (invite_only == enabled)
		return (false);
	invite_only = enabled;
	return (true);
}

bool	Channel::is_invite_only() const
{
	return (invite_only);
}

bool	Channel::set_topic_restricted(bool enabled)
{
	if (topic_restricted == enabled)
		return (false);
	topic_restricted = enabled;
	return (true);
}

bool	Channel::is_topic_restricted() const
{
	return (topic_restricted);
}

bool	Channel::set_key(const Wire &key)
{
	if (key_enabled && channel_key == key)
		return (false);
	channel_key = key;
	key_enabled = true;
	return (true);
}

bool	Channel::clear_key()
{
	if (!key_enabled)
		return (false);
	channel_key.clear();
	key_enabled = false;
	return (true);
}

bool	Channel::has_key() const
{
	return (key_enabled);
}

Wire	Channel::get_key() const
{
	return (channel_key);
}

bool	Channel::set_user_limit(size_t limit)
{
	if (limit_enabled && user_limit == limit)
		return (false);
	user_limit = limit;
	limit_enabled = true;
	return (true);
}

bool	Channel::clear_user_limit()
{
	if (!limit_enabled)
		return (false);
	user_limit = 0;
	limit_enabled = false;
	return (true);
}

bool	Channel::has_user_limit() const
{
	return (limit_enabled);
}

size_t	Channel::get_user_limit() const
{
	return (user_limit);
}

Set<int>	Channel::get_member_fds() const
{
	return (member_fds);
}

bool	Channel::empty() const
{
	return (member_fds.empty());
}

void	Channel::broadcast(const Wire &message, int except_fd) const
{
	member_fds.subtract(except_fd).forEach(send_string_fn, message, server);
}

void	Channel::broadcast(const Client &client, const Wire &cmd, const Wire &param) const
{
	broadcast(make_msg(client, cmd, name, param));
}

void	Channel::broadcast_from(const Client &client, const Wire &cmd, const Wire &param) const
{
	broadcast(make_msg(client, cmd, name, param), client.get_socket());
}

