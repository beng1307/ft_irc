#include "Client.hpp"
#include "../helpers/print.hpp"
#include "../helpers/Wire.hpp"
#include "../Server/Server.hpp"


///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Client::Client():
	server(NULL), socket(0), password(""), username(""),
	nickname(""), pass_ok(false), is_registered(false), is_admin(false),
	close_after_output(false), buffer(""), out_buffer("")
{
	_ok = false;
	return ;
}

Client::Client(int socket, Server *server):
	server(server), socket(socket), password(""), username(""),
	nickname(""), pass_ok(false), is_registered(false), is_admin(false),
	close_after_output(false), buffer(""), out_buffer("")
{
	_ok = true;
	return ;
}

Client::Client(const Client &other):
	server(other.server), socket(other.socket), password(other.password),
	username(other.username), nickname(other.nickname),
	pass_ok(other.pass_ok), is_registered(other.is_registered), is_admin(other.is_admin),
	close_after_output(other.close_after_output),
	buffer(other.buffer), out_buffer(other.out_buffer)
{
	_ok = other._ok;
	return ;
}

Client	&Client::operator=(const Client &other)
{
	if (this != &other)
	{
		server = other.server;
		socket = other.socket;
		nickname = other.nickname;
		username = other.username;
		password = other.password;
		pass_ok = other.pass_ok;
		is_registered = other.is_registered;
		is_admin = other.is_admin;
		close_after_output = other.close_after_output;
		buffer = other.buffer;
		out_buffer = other.out_buffer;
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

void	Client::send(Wire message)
{
	if (!server)
		return ;
	if (!message.empty() && (message.length() < 2 || message.substr(message.length() - 2) != "\r\n"))
		message += "\r\n";
	server->send_to_client(socket, message);
}


///////////////////////////////////////////////////////////////////////////////
// Setter & Getter

void	Client::set_server(Server *server)
{
	this->server = server;
}

Server	*Client::get_server() const
{
	return (server);
}

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

void	Client::append_raw_buffer(const char *data, size_t size)
{
	buffer.append(data, size);
}

void	Client::append_buffer(const Wire &data)
{
	buffer += data;
}

void	Client::set_out_buffer(const Wire &out_buffer)
{
	this->out_buffer = out_buffer;
}

Wire	&Client::get_out_buffer()
{
	return (out_buffer);
}

Wire	Client::get_out_buffer() const
{
	return (out_buffer);
}

void	Client::set_close_after_output(bool close_after_output)
{
	this->close_after_output = close_after_output;
}

bool	Client::get_close_after_output() const
{
	return (close_after_output);
}
