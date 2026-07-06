#include "Server.hpp"
#include "Channel.hpp"
#include "Client.hpp"
#include "Errorhandler.hpp"
#include <iostream>
#include <string>
#include <cstdlib>


int main(int ac, char **av)
{
	if (!Errorhandler::right_amount_of_args(ac))
	{
		std::cout << "Expected input: \"./ircserv <port> <password>\"";
		return (1);
	}

	std::string		password(av[2]);
	unsigned int	port = (unsigned int)atoi(av[1]);

	Server server(port, password);

	server.socket_setup();
	server.server_loop();

	return (0);
}