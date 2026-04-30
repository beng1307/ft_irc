#ifndef SERVER_HPP
# define SERVER_HPP

#include <string>

class Server
{
	public:

	///////////////////////////////////////////////////////////////////////////////
	// Public Constructors and destructor

		Server();
		Server(int port, std::string password);
		Server &operator=(Server &other);
		Server(Server &other);

	///////////////////////////////////////////////////////////////////////////////
	// Public Variables

	unsigned int	port;
	std::string		password;

	int  			server_socket;

	///////////////////////////////////////////////////////////////////////////////
	// Public Methods

	int socket_setup();
	int server_loop();
};

#endif
