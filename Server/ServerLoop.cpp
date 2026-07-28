

void	Server::server_loop()
{
	//Makes the Server nonblocking by saving the flags and add O_NONBLOCK to the flags.
	int flags = fcntl(server_socket, F_GETFL, 0);
	if (flags == -1)
	{
		std::cerr << "Error: fcntl failed!" << std::endl;
		return;
	}

	if (fcntl(server_socket, F_SETFL, flags | O_NONBLOCK) == -1)
	{
		std::cerr << "Error: fcntl failed!" << std::endl;
		return;
	}

	//Adds the server socket to the poll file descriptors
	add_fds(server_socket, POLLIN, 0);

	// Server loop that continuously checks for events
	while (true)
	{
		int ready = poll(fds.data(), fds.size(), -1);
		if (ready == -1)
		{
			if (errno == EINTR)
				continue;
			std::cerr << "Error: poll failed!" << std::endl;
			break;
		}

		// Goes through all the file descriptors and checks if there are events to handle
		for (size_t index = 0; index < fds.size(); ++index)
		{
			if (fds[index].revents & POLLIN)
			{
				if (fds[index].fd == server_socket)
				{
					int client_socket = accept(server_socket, NULL, NULL);
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
					clients.insert(std::make_pair(client_socket, Client(client_socket)));
				}
				else
				{
					char	buffer[512];

					while (true)
					{
						int	bytes_received = recv(fds[index].fd, buffer, sizeof(buffer) - 1, 0);
						if (bytes_received > 0)
						{
							buffer[bytes_received] = '\0';
							clients[fds[index].fd].get_buffer().append(buffer, bytes_received);

							size_t	position = clients[fds[index].fd].get_buffer().find("\r\n");

							while (position != std::string::npos)
							{
								handle_line(clients[fds[index].fd], position);
								position = clients[fds[index].fd].get_buffer().find("\r\n");
							}

							if (clients.find(fds[index].fd) != clients.end())
								std::cout << "Received from client " << fds[index].fd << ": " << buffer << std::endl;
						}
						else if (bytes_received == 0)
						{
							int disconnected_fd = fds[index].fd;
							cleanup_client_disconnect(disconnected_fd);
							close(fds[index].fd);
							clients.erase(fds[index].fd);
							fds.erase(fds.begin() + index);
							--index;
							break ;
						}
						else
						{
							if (errno == EAGAIN || errno == EWOULDBLOCK)
								break ;

							int disconnected_fd = fds[index].fd;
							cleanup_client_disconnect(disconnected_fd);
							close(fds[index].fd);
							clients.erase(fds[index].fd);
							fds.erase(fds.begin() + index);
							--index;
							break ;
						}
					}
				}
			}
		}
	}
}
