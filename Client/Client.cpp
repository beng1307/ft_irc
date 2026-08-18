#include "Client.hpp"
#include <iostream>
#include <string>
#include "../helpers/print.hpp"
#include "../helpers/Wire.hpp"


///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Client::Client():
	socket(0), password(""), username(""),
	nickname(""), pass_ok(false), is_registered(false), is_admin(false),
	buffer("")
{
	_ok = false;
	return ;
}

Client::Client(int socket):
	socket(socket), password(""), username(""),
	nickname(""), pass_ok(false), is_registered(false), is_admin(false),
	buffer("")
{
	_ok = true;
	return ;
}

Client::Client(const Client &other):
	socket(other.socket), password(other.password),
	username(other.username), nickname(other.nickname),
	pass_ok(other.pass_ok), is_registered(other.is_registered), is_admin(other.is_admin),
	buffer(other.buffer)
{
	_ok = other._ok;
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
		pass_ok = other.pass_ok;
		is_registered = other.is_registered;
		is_admin = other.is_admin;
		buffer = other.buffer;
		_ok = other._ok;
	}
	return (*this);
}


///////////////////////////////////////////////////////////////////////////////
// Methods & helper functions

void	Client::register_client(const Wire &password)
{
	if (this->password == password && !nickname.empty() && !username.empty())
	{
		print("Client ", nickname, " registered successfully!");
		this->is_registered = true;
	}
}


///////////////////////////////////////////////////////////////////////////////
// Setter & Getter

void	Client::set_socket(const int &socket)
{
	this->socket = socket;
}

int	Client::get_socket() const
{
	return (socket);
}


void	Client::set_password(const Wire &password)
{
	this->password = password;
}

Wire	Client::get_password() const
{
	return (password);
}

void	Client::set_pass_ok(const bool &pass_ok)
{
	this->pass_ok = pass_ok;
}

bool	Client::get_pass_ok() const
{
	return (pass_ok);
}


void	Client::set_username(const Wire &username)
{
	this->username = username;
}

Wire	Client::get_username() const
{
	return (username);
}


void	Client::set_nickname(const Wire &nickname)
{
	this->nickname = nickname;
}

Wire	Client::get_nickname() const
{
	return (nickname);
}


void	Client::set_admin_status(const bool &admin_status)
{
	this->is_admin = admin_status;
}

bool	Client::get_admin_status() const
{
	return (is_admin);
}


void	Client::set_register_status(const bool &register_status)
{
	this->is_registered = register_status;
}

bool	Client::get_register_status() const
{
	return (is_registered);
}

void	Client::set_buffer(const Wire &buffer)
{
	this->buffer = buffer;
}

Wire	&Client::get_buffer()
{
	return (buffer);
}

Wire	Client::get_buffer() const
{
	return (buffer);
}
