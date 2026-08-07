#include "Server.hpp"
#include <fcntl.h>
#include <poll.h>
#include <unistd.h>
#include <cerrno>
#include <iostream>
#include <sys/socket.h>
#include <cstring>


bool	Server::configure_socket_nonblocking(int socket)
{
	int flags = fcntl(socket, F_GETFL, 0);
	if (flags == -1)
	{
		std::cerr << "Error: fcntl failed!" << std::endl;
		return false;
	}

	if (fcntl(socket, F_SETFL, flags | O_NONBLOCK) == -1)
	{
		std::cerr << "Error: fcntl failed!" << std::endl;
		return false;
	}
	return true;
}

void	Server::accept_new_client(int client_socket)
{
	if (!configure_socket_nonblocking(client_socket))
	{
		close(client_socket);
		return;
	}

	add_fds(client_socket, POLLIN, 0);
	get_clients().insert(std::make_pair(client_socket, Client(client_socket)));
}

void	Server::handle_client_input(int client_fd, size_t &index)
{
	char	buffer[512];

	while (true)
	{
		int	bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
		if (bytes_received > 0)
		{
			buffer[bytes_received] = '\0';
			Client &client = get_clients()[client_fd];
			client.get_buffer().append(buffer, bytes_received);

			size_t	position = client.get_buffer().find("\r\n");
			while (position != std::string::npos)
			{
				handle_line(client, position);
				position = client.get_buffer().find("\r\n");
			}

			std::cout << "Received from client " << client_fd << ": " << buffer << std::endl;
		}
		else if (bytes_received == 0)
		{
			disconnect_client(client_fd, index);
			break ;
		}
		else
		{
			if (errno == EAGAIN || errno == EWOULDBLOCK)
				break ;

			disconnect_client(client_fd, index);
			break ;
		}
	}
}

void	Server::disconnect_client(int client_fd, size_t &index)
{
	cleanup_client_disconnect(client_fd);
	close(client_fd);
	get_clients().erase(client_fd);
	get_fds().erase(get_fds().begin() + index);
	--index;
}

void	Server::server_loop()
{
	if (!configure_socket_nonblocking(get_server_socket()))
		return;

	add_fds(get_server_socket(), POLLIN, 0);

	while (true)
	{
		int ready = poll(get_fds().data(), get_fds().size(), -1);
		if (ready == -1)
		{
			if (errno == EINTR)
				continue;
			std::cerr << "Error: poll failed!" << std::endl;
			break;
		}

		for (size_t index = 0; index < get_fds().size(); ++index)
		{
			if (!(get_fds()[index].revents & POLLIN))
				continue;

			if (get_fds()[index].fd == get_server_socket())
			{
				int client_socket = accept(get_server_socket(), NULL, NULL);
				if (client_socket == -1)
				{
					std::cerr << "Error: accept failed!" << std::endl;
					continue;
				}
				accept_new_client(client_socket);
			}
			else
				handle_client_input(get_fds()[index].fd, index);
		}
	}
}
