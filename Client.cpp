#include "Client.hpp"
#include <iostream>
#include <string>


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


///////////////////////////////////////////////////////////////////////////////
// Methods & helper functions

void	Client::register_client(const std::string &password)
{
	if (this->password == "password" && !nickname.empty() && !username.empty())
	{
		std::cout << "Client " << nickname << " registered successfully!" << std::endl;
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


void	Client::set_password(const std::string &password)
{
	this->password = password;

	register_client(password);
}

std::string	Client::get_password() const
{
	return (password);
}


void	Client::set_username(const std::string &username)
{
	this->username = username;

	register_client(password);
}

std ::string	Client::get_username() const
{
	return (username);
}


void	Client::set_nickname(const std::string &nickname)
{
	this->nickname = nickname;

	register_client(password);
}

std::string	Client::get_nickname() const
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


void	Client::set_buffer(const std::string &buffer)
{
	this->buffer = buffer;
}

std::string	Client::get_buffer() const
{
	return (buffer);
}
