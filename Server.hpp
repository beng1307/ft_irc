#ifndef SERVER_HPP
# define SERVER_HPP

#include "Client.hpp"
#include "Channel.hpp"
#include <string>
#include <map>
#include <vector>
#include <poll.h>


class Server
{
	private:

	public:

		///////////////////////////////////////////////////////////////////////////////
		// Constructors and destructor

		Server();
		Server(int port, std::string password);
		Server &operator=(const Server &other);
		Server(const Server &other);
		~Server();

		///////////////////////////////////////////////////////////////////////////////
		// Variables

		//TODO: Make variables private and add getter and setter if needed
		unsigned int				port;
		std::string					password;

		int  						server_socket;

		std::map<int, Client>		clients; //Check if map is the best option for this, maybe change to vector or list
		std::vector<Channel>		channels; //Same apllies here, maybe change to map with channel name as key
		std::vector<pollfd>			fds;


		///////////////////////////////////////////////////////////////////////////////
		// Methods

		int							socket_setup();
		void						server_loop();
		void						add_fds(int fd, short events, short revents);
		void						handle_line(Client &client, const size_t &position);
		bool						is_command(const std::string &line);


		// void 						handle_kick();
		// void 						handle_invite();
		// void 						handle_topic();
		// void 						handle_mode();
		void						join_channel(const std::string &channel_name);
		// void						send_message_to_channel(const std::string &line);
		std::vector<std::string>	split_arguments(const std::string &line);

};

#endif
