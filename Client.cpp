#include "Client.hpp"

///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Client::Client():
	socket(0), nickname(""), username(""),
	password(""), is_registered(false), is_admin(false),
	buffer("")
{
	return ;
}

Client::Client(int socket):
	socket(socket), nickname(""), username(""),
	password(""), is_registered(false), is_admin(false),
	buffer("")
{
	return ;
}

Client::Client(const Client &other):
	socket(other.socket), nickname(other.nickname),
	username(other.username), password(other.password),
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
		password = other.password;
		is_registered = other.is_registered;
		is_admin = other.is_admin;
		buffer = other.buffer;
	}
	return (*this);
}

void	Client::set_socket(const int &socket)
{
	this->socket = socket;
}

void	Client::set_password(const std::string &password)
{
	this->password = password;
}

void	Client::set_username(const std::string &username)
{
	this->username = username;
}

void	Client::set_nickname(const std::string &nickname)
{
	this->nickname = nickname;
}

void	Client::set_admin_status(const bool &admin_status)
{
	this->is_admin = admin_status;
}

void	Client::set_register_status(const bool &register_status)
{
	this->is_registered = register_status;
}

void	Client::set_buffer(const std::string &buffer)
{
	this->buffer = buffer;
}