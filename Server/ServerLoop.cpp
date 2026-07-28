#include "Server.hpp"
#include <fcntl.h>
#include <poll.h>
#include <unistd.h>
#include <cerrno>
#include <iostream>
#include <sys/socket.h>
#include <cstring>


void	Server::server_loop()
{
	//Makes the Server nonblocking by saving the flags and add O_NONBLOCK to the flags.
	int flags = fcntl(get_server_socket(), F_GETFL, 0);
	if (flags == -1)
	{
		std::cerr << "Error: fcntl failed!" << std::endl;
		return;
	}

	if (fcntl(get_server_socket(), F_SETFL, flags | O_NONBLOCK) == -1)
	{
		std::cerr << "Error: fcntl failed!" << std::endl;
		return;
	}

	//Adds the server socket to the poll file descriptors
	add_fds(get_server_socket(), POLLIN, 0);

	// Server loop that continuously checks for events
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

		// Goes through all the file descriptors and checks if there are events to handle
		for (size_t index = 0; index < get_fds().size(); ++index)
		{
			if (get_fds()[index].revents & POLLIN)
			{
				if (get_fds()[index].fd == get_server_socket())
				{
					int client_socket = accept(get_server_socket(), NULL, NULL);
					if (client_socket == -1)
					{
					    std::cerr << "Error: accept failed!" << std::endl;
					    continue;
					}

					if (fcntl(client_socket, F_SETFL, flags | O_NONBLOCK) == -1)
					{
					    std::cerr << "Error: fcntl failed!" << std::endl;
					    close(client_socket);
					    continue;
					}

					add_fds(client_socket, POLLIN, 0);
					get_clients().insert(std::make_pair(client_socket, Client(client_socket)));
				}
				else
				{
					char	buffer[512];

					while (true)
					{
						int	bytes_received = recv(get_fds()[index].fd, buffer, sizeof(buffer) - 1, 0);
						if (bytes_received > 0)
						{
							buffer[bytes_received] = '\0';
							get_clients()[get_fds()[index].fd].get_buffer().append(buffer, bytes_received);

							size_t	position = get_clients()[get_fds()[index].fd].get_buffer().find("\r\n");

							while (position != std::string::npos)
							{
								handle_line(get_clients()[get_fds()[index].fd], position);
								position = get_clients()[get_fds()[index].fd].get_buffer().find("\r\n");
							}

							if (get_clients().find(get_fds()[index].fd) != get_clients().end())
							std::cout << "Received from client " << get_fds()[index].fd << ": " << buffer << std::endl;
						}
						else if (bytes_received == 0)
						{
							int disconnected_fd = get_fds()[index].fd;
							cleanup_client_disconnect(disconnected_fd);
							close(get_fds()[index].fd);
							get_clients().erase(get_fds()[index].fd);
							get_fds().erase(get_fds().begin() + index);
							--index;
							break ;
						}
						else
						{
							if (errno == EAGAIN || errno == EWOULDBLOCK)
								break ;

							int disconnected_fd = get_fds()[index].fd;
							cleanup_client_disconnect(disconnected_fd);
							close(get_fds()[index].fd);
							get_clients().erase(get_fds()[index].fd);
							get_fds().erase(get_fds().begin() + index);
							--index;
							break ;
						}
					}
				}
			}
		}
	}
}
