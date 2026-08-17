#ifndef SERVER_HPP
# define SERVER_HPP

#include "../Client/Client.hpp"
#include "../Channel/Channel.hpp"
#include "../helpers/Wire.hpp"
#include <map>
#include <vector>
#include <poll.h>


typedef std::map<Wire, Channel> ChannelMap;
typedef std::map<int, Client>   ClientMap;

class Server
{
	private:

		///////////////////////////////////////////////////////////////////////////////
		// Variables

		unsigned int		port;
		Wire				password;

		int					server_socket;

		ClientMap			clients;
		ChannelMap			channels;
		std::vector<pollfd>	fds;

		///////////////////////////////////////////////////////////////////////////////
		// Helper methods for the main loop

		bool configure_socket_nonblocking(int socket);
		void accept_new_client(int client_socket);
		void handle_client_input(int client_fd);
		void disconnect_client(int client_fd);

	public:

		///////////////////////////////////////////////////////////////////////////////
		// Constructors and destructor

		Server();
		Server(int port, Wire password);
		Server &operator=(const Server &other);
		Server(const Server &other);
		~Server();

		///////////////////////////////////////////////////////////////////////////////
		// Getter and Setter

		void set_port(unsigned int port);
		unsigned int get_port() const;

		void set_password(const Wire &password);
		Wire get_password() const;

		void set_server_socket(int socket);
		int get_server_socket() const;

		void set_clients(const ClientMap &clients);
		ClientMap &get_clients();
		const ClientMap &get_clients() const;

		void set_channels(const ChannelMap &channels);
		ChannelMap &get_channels();
		const ChannelMap &get_channels() const;

		void set_fds(const std::vector<pollfd> &fds);
		std::vector<pollfd> &get_fds();
		const std::vector<pollfd> &get_fds() const;

		///////////////////////////////////////////////////////////////////////////////
		// Methods

		int socket_setup();
		void server_loop();
		void add_fds(int fd, short events, short revents);
		void handle_line(Client &client, const size_t &position);
		void dispatch_command(Client &client, const Wire &command, const Wire &line, const std::vector<Wire> &arguments);
		void handle_pass_command(Client &client, const std::vector<Wire> &arguments);
		void handle_user_command(Client &client, const std::vector<Wire> &arguments);
		void handle_nick_command(Client &client, const std::vector<Wire> &arguments);
		void handle_join_command(Client &client, const std::vector<Wire> &arguments);
		void handle_part_command(Client &client, const Wire &line, const std::vector<Wire> &arguments);
		void handle_cap_command(Client &client, const std::vector<Wire> &arguments);
		void handle_privmsg_command(Client &client, const Wire &line, const std::vector<Wire> &arguments);
		void handle_ping_command(Client &client, const std::vector<Wire> &arguments);
		void handle_quit_command(Client &client, const Wire &line, const std::vector<Wire> &arguments);
		bool is_command(const Wire &line);
		void try_register_client(Client &client);
		Wire to_string_size_t(size_t value);
		bool is_positive_number(const Wire &value);
		bool is_valid_nickname(const Wire &nickname);
		void handle_kick(Client &client, const Wire &line, const std::vector<Wire> &arguments);
		void handle_invite(Client &client, const std::vector<Wire> &arguments);
		void handle_topic(Client &client, const Wire &line, const std::vector<Wire> &arguments);
		void handle_mode(Client &client, const Wire &line, const std::vector<Wire> &arguments);
		void let_client_join_channel(const Wire &channel_name, Client &client, const Wire &key);
		void part_client_from_channel(Client &client, const Wire &channel_name, const Wire &reason);
		void send_message_to_channel(Client &sender, const Wire &channel_name, const Wire &message);
		void broadcast_join_to_channel(Client &joining_client, const Wire &channel_name);
		void broadcast_part_to_channel(Client &parting_client, const Wire &channel_name, const Wire &reason);
		void broadcast_to_channel(const Channel &channel, const Wire &message);

		void send_message_to_user(Client &sender, const Wire &nickname, const Wire &message);
		void send_status(Client &client, const Wire &code, const Wire &message);
		void send_channel_names_reply(Client &client, const Wire &channel_name);
		Client *find_client_by_nickname(const Wire &nickname);
		std::vector<Wire> split_arguments(const Wire &line);

};

Wire	make_msg(const Client &client, const Wire &cmd, const Wire &target, const Wire &param = "");
ssize_t	send_string(int fd, const Wire &str);
ssize_t	send_msg(int fd, const Client &client, const Wire &cmd, const Wire &target, const Wire &param = "");

#endif

