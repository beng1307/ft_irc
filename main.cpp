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

	std::string password(av[2]);
	Server server((unsigned int)atoi(av[1]), password);

	server.socket_setup();
	server.server_loop();

	return (0);
}