#include "Server/Server.hpp"
#include "Channel/Channel.hpp"
#include "Client/Client.hpp"
#include <iostream>
#include <string>
#include <cstdlib>
#include "helpers/print.hpp"
#include "helpers/Wire.hpp"


int main(int ac, char **av)
{
	if (ac != 3)
	{
		print("Expected input: \"./ircserv <port> <password>\"");
		return (1);
	}

	Wire			password(av[2]);
	unsigned int	port = (unsigned int)atoi(av[1]);

	Server server(port, password);

	server.socket_setup();
	server.server_loop();

	return (0);
}