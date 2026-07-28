#ifndef SERVER_HPP
# define SERVER_HPP

#include "Client.hpp"
#include "Channel.hpp"
#include <string>
#include <map>
#include <vector>
#include <poll.h>

typedef std::map<std::string, Channel>	ChannelMap;
typedef std::map<int, Client> 			ClientMap;

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
		unsigned int					port;
		std::string						password;

		int  							server_socket;

		ClientMap						clients; //Check if map is the best option for this, maybe change to vector or list
		ChannelMap						channels; //Same applies here, maybe change to map with channel name as key
		std::vector<pollfd>				fds;


		///////////////////////////////////////////////////////////////////////////////
		// Methods

		int								socket_setup();
		void							server_loop();
		void							add_fds(int fd, short events, short revents);
		void							handle_line(Client &client, const size_t &position);
		bool							is_command(const std::string &line);
		void							try_register_client(Client &client);


		void							handle_kick(Client &client, const std::string &line,
											 const std::vector<std::string> &arguments);
		void						handle_invite(Client &client,
									  const std::vector<std::string> &arguments);
		void						handle_topic(Client &client, const std::string &line,
									 const std::vector<std::string> &arguments);
		void					handle_mode(Client &client, const std::string &line,
								 const std::vector<std::string> &arguments);
		void					let_client_join_channel(const std::string &channel_name, Client &client, const std::string &key);
		void							part_client_from_channel(Client &client, const std::string &channel_name);
		void							send_message_to_channel(Client &sender, const std::string &channel_name, const std::string &message);
		void							send_message_to_user(Client &sender, const std::string &nickname, const std::string &message);
		void							send_welcome_message(Client &client);
		void							send_error_reply(Client &client, const std::string &code, const std::string &message);
		void							cleanup_client_disconnect(int disconnected_fd);
		Client							*find_client_by_nickname(const std::string &nickname);
		std::vector<std::string>		split_arguments(const std::string &line);

};

#endif
