#include "Client.hpp"

///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Client::Client(): socket(0), nickname(""), username(""), realname("")
{
	return ;
}

Client::Client(int socket): socket(socket), nickname(""), username(""), realname("")
{
	return ;
}

Client::Client(Client &other): socket(other.socket), nickname(other.nickname), username(other.username), realname(other.realname)
{
	return ;
}

Client	&Client::operator=(Client &other)
{
	if (this != &other)
	{
		socket = other.socket;
		nickname = other.nickname;
		username = other.username;
		realname = other.realname;
	}
	return (*this);
}

