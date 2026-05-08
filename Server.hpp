#ifndef SERVER_HPP
# define SERVER_HPP

#include "Client.hpp"
#include <string>
#include <map>
#include <vector>
#include <poll.h>



class Server
{
	public:

	///////////////////////////////////////////////////////////////////////////////
	// Public Constructors and destructor

	Server();
	Server(int port, std::string password);
	Server &operator=(const Server &other);
	Server(const Server &other);

	///////////////////////////////////////////////////////////////////////////////
	// Public Variables

	unsigned int			port;
	std::string				password;

	int  					server_socket;

	std::map<int, Client>	clients;
	std::vector<pollfd>		fds;



	///////////////////////////////////////////////////////////////////////////////
	// Public Methods

	int		socket_setup();
	void	server_loop();
	void	add_fds(int fd, short events, short revents);
	void	handle_line(Client &client, const size_t &position);
	bool	is_command(const std::string &line);

	void	kick();
	void	invite();
	void	topic();
	void	mode();
	void	send_message_to_channel(const std::string &line);
};

#endif
