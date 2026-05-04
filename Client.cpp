#include "Client.hpp"

///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Client::Client():
	socket(0), nickname(""), username(""),
	realname(""), is_registered(false), is_admin(false),
	buffer("")
{
	return ;
}

Client::Client(int socket):
	socket(socket), nickname(""), username(""),
	realname(""), is_registered(false), is_admin(false),
	buffer("")
{
	return ;
}

Client::Client(const Client &other):
	socket(other.socket), nickname(other.nickname),
	username(other.username), realname(other.realname),
	is_registered(other.is_registered), is_admin(other.is_admin),
	buffer(other.buffer)
	{
	return ;
}

Client	&Client::operator=(const Client &other)
{
	if (this != &other)
	{
		socket = other.socket;
		nickname = other.nickname;
		username = other.username;
		realname = other.realname;
		is_registered = other.is_registered;
		is_admin = other.is_admin;
		buffer = other.buffer;
	}
	return (*this);
}

