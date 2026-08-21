#include "Server.hpp"
#include "../Client/Client.hpp"
#include "../Channel/Channel.hpp"
#include "../helpers/Wire.hpp"
#include "../helpers/Int.hpp"
#include <unistd.h>


///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

Server::Server():
	port(0), password(""), server_socket(), epoll_fd(), clients(), channels()
{
	return ;
}

Server::Server(int port, Wire password):
	port(port), password(password), server_socket(), epoll_fd(), clients(), channels()
{
	return ;
}

Server::Server(const Server &other): port(other.port), password(other.password),
	server_socket(other.server_socket), epoll_fd(other.epoll_fd), clients(other.clients), channels(other.channels)
{
	return ;
}

Server	&Server::operator=(const Server &other)
{
	if (this != &other)
	{
		port = other.port;
		password = other.password;
		server_socket = other.server_socket;
		epoll_fd = other.epoll_fd;
		clients = other.clients;
		channels = other.channels;
	}
	return (*this);
}

// Destructor:
// Rationale: Provides RAII cleanup guarantee. If the Server object is destroyed
// (e.g. stack unwinding on early return or exception), ensure any still-open
// server listening socket descriptor and epoll instance are closed.
Server::~Server()
{
	if (server_socket && server_socket >= 0)
	{
		close(server_socket);
		server_socket.notok();
	}
	if (epoll_fd && epoll_fd >= 0)
	{
		close(epoll_fd);
		epoll_fd.notok();
	}
}

///////////////////////////////////////////////////////////////////////////////
// Getter and Setter

void	Server::set_port(unsigned int port)
{
	this->port = port;
}

unsigned int	Server::get_port() const
{
	return (port);
}

void	Server::set_password(const Wire &password)
{
	this->password = password;
}

Wire	Server::get_password() const
{
	return (password);
}

void	Server::set_server_socket(Fd socket)
{
	this->server_socket = socket;
}

Fd	Server::get_server_socket() const
{
	return (server_socket);
}

void	Server::set_clients(const ClientMap &clients)
{
	this->clients = clients;
}

ClientMap	&Server::get_clients()
{
	return (clients);
}

const ClientMap	&Server::get_clients() const
{
	return (clients);
}

Client	&Server::get_client(Fd fd)
{
	return (clients.fetch(fd));
}

const Client	&Server::get_client(Fd fd) const
{
	return (clients.fetch(fd));
}

static bool	match_nickname(const Client &c, const Wire &nick)
{
	return (c.get_nickname() == nick);
}

Client	&Server::get_client(const Wire &nickname)
{
	return (clients.fetch(match_nickname, nickname));
}

const Client	&Server::get_client(const Wire &nickname) const
{
	return (clients.fetch(match_nickname, nickname));
}

void	Server::add_client(Fd socket)
{
	clients[socket] = Client(socket);
}

void	Server::remove_client(Fd socket)
{
	clients.erase(socket);
}

void	Server::set_channels(const ChannelMap &channels)
{
	this->channels = channels;
}

ChannelMap	&Server::get_channels()
{
	return (channels);
}

const ChannelMap	&Server::get_channels() const
{
	return (channels);
}

Channel	&Server::get_channel(const Wire &name)
{
	return (channels.fetch(name));
}

const Channel	&Server::get_channel(const Wire &name) const
{
	return (channels.fetch(name));
}

void	Server::add_channel(const Channel &channel)
{
	channels[channel.get_name()] = channel;
}

void	Server::remove_channel(const Wire &channel_name)
{
	channels.erase(channel_name);
}

void	Server::set_epoll_fd(Fd epoll_fd)
{
	this->epoll_fd = epoll_fd;
}

Fd		Server::get_epoll_fd() const
{
	return (epoll_fd);
}
