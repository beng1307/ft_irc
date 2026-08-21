#ifndef SERVER_HPP
# define SERVER_HPP

#include "../Client/Client.hpp"
#include "../Channel/Channel.hpp"
#include "../helpers/Wire.hpp"
#include "../helpers/Vector.hpp"
#include "../helpers/Set.hpp"
#include "../helpers/Map.hpp"
#include "../helpers/Int.hpp"
#include <sys/epoll.h>

// Global execution control flag (defined in main.cpp, used by ServerLoop.cpp)
// Set to false on SIGINT / SIGTERM to trigger graceful event-loop termination.
extern bool g_running;

typedef Map<Wire, Channel> ChannelMap;
typedef Map<Fd, Client>     ClientMap;

class Server
{
	private:

		///////////////////////////////////////////////////////////////////////////////
		// Variables

		unsigned int		port;
		Wire				password;

		Fd					server_socket;
		Fd					epoll_fd;

		ClientMap			clients;
		ChannelMap			channels;

		///////////////////////////////////////////////////////////////////////////////
		// Helper methods for the main loop

		bool configure_socket_nonblocking(Fd socket);
		void accept_new_client(Fd client_socket);
		void handle_client_input(Fd client_fd);
		void disconnect_client(Fd client_fd);

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

		void set_server_socket(Fd socket);
		Fd get_server_socket() const;

		void set_epoll_fd(Fd epoll_fd);
		Fd get_epoll_fd() const;

		void set_clients(const ClientMap &clients);
		ClientMap &get_clients();
		const ClientMap &get_clients() const;
		Client &get_client(Fd fd);
		const Client &get_client(Fd fd) const;
		Client &get_client(const Wire &nickname);
		const Client &get_client(const Wire &nickname) const;
		void add_client(Fd socket);
		void remove_client(Fd socket);

		void set_channels(const ChannelMap &channels);
		ChannelMap &get_channels();
		const ChannelMap &get_channels() const;
		Channel &get_channel(const Wire &name);
		const Channel &get_channel(const Wire &name) const;
		void add_channel(const Channel &channel);
		void remove_channel(const Wire &channel_name);

		///////////////////////////////////////////////////////////////////////////////
		// Methods

		int socket_setup();
		void server_loop();
		void add_epoll_fd(Fd fd, uint32_t events);
		void remove_epoll_fd(Fd fd);
		void handle_line(Client &client, const size_t &position);
		void dispatch_command(Client &client, const Wire &command, const Wire &line, const Vector<Wire> &arguments);
		void handle_pass_command(Client &client, const Vector<Wire> &arguments);
		void handle_user_command(Client &client, const Vector<Wire> &arguments);
		void handle_nick_command(Client &client, const Vector<Wire> &arguments);
		void handle_join_command(Client &client, const Vector<Wire> &arguments);
		void handle_part_command(Client &client, const Wire &line, const Vector<Wire> &arguments);
		void handle_cap_command(Client &client, const Vector<Wire> &arguments);
		void handle_privmsg_command(Client &client, const Wire &line, const Vector<Wire> &arguments);
		void handle_ping_command(Client &client, const Vector<Wire> &arguments);
		void handle_quit_command(Client &client, const Wire &line, const Vector<Wire> &arguments);
		bool is_command(const Wire &line);
		void try_register_client(Client &client);
		bool is_positive_number(const Wire &value);
		bool is_valid_nickname(const Wire &nickname);
		void handle_kick(Client &client, const Wire &line, const Vector<Wire> &arguments);
		void handle_invite(Client &client, const Vector<Wire> &arguments);
		void handle_topic(Client &client, const Wire &line, const Vector<Wire> &arguments);
		void handle_mode(Client &client, const Wire &line, const Vector<Wire> &arguments);
		Channel &ensure_channel_exists(Client &client, const Wire &channel_name);
		bool ensure_channel_member(Client &client, Channel &channel);
		bool ensure_channel_operator(Client &client, Channel &channel);
		void let_client_join_channel(const Wire &channel_name, Client &client, const Wire &key);
		void part_client_from_channel(Client &client, const Wire &channel_name, const Wire &reason);
		void send_message_to_channel(Client &sender, const Wire &channel_name, const Wire &message);

		void send_message_to_user(Client &sender, const Wire &nickname, const Wire &message);
		void send_status(Client &client, const Wire &code, const Wire &message);
		void send_channel_names_reply(Client &client, const Wire &channel_name);
		Vector<Wire> split_arguments(const Wire &line);
		Set<Fd> get_client_audience(Fd client_fd) const;

};
Wire	make_msg(const Client &client, const Wire &cmd, const Wire &target, const Wire &param = "");
ssize_t	send_string(Fd fd, const Wire &str);
ssize_t	send_msg(Fd fd, const Client &client, const Wire &cmd, const Wire &target, const Wire &param = "");


#endif

