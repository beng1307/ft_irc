#ifndef CHANNEL_HPP
# define CHANNEL_HPP

#include "../Client/Client.hpp"
#include "../helpers/Wire.hpp"
#include "../helpers/Set.hpp"


class Server;

class	Channel
{
	private:

///////////////////////////////////////////////////////////////////////////////
// Variables

		Server				*server;
		Wire				name;
		Wire				topic;

		Set<int> 		member_fds;
		Set<int> 		operator_fds;
		Set<int> 		invited_fds;

		bool				invite_only;
		bool				topic_restricted;

		bool				key_enabled;
		Wire				channel_key;
		bool				limit_enabled;
		size_t				user_limit;


	public:

		OK_CHECK(Channel);

///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

		Channel();
		Channel(const Wire &name, Server *server = NULL);
		Channel(const Channel &other);
		Channel &operator=(const Channel &other);
		~Channel();


///////////////////////////////////////////////////////////////////////////////
// Setter, Getter & Helper

		void				set_server(Server *server);
		Server				*get_server() const;

		void				set_name(const Wire &name);
		Wire				get_name() const;

		void				set_topic(const Wire &topic);
		Wire				get_topic() const;
		
		Wire				get_key() const;
		size_t				get_user_limit() const;
		
		Set<int>		get_member_fds() const;
		bool				empty() const;

		bool				set_invite_only(bool enabled);
		bool				set_topic_restricted(bool enabled);
		bool				set_key(const Wire &key);
		bool				clear_key();
		bool				set_user_limit(size_t limit);
		bool				clear_user_limit();

		void				add_member(int client_fd);
		bool				has_member(int client_fd) const;
		void				remove_client_from_channel(int client_fd);
		void				remove_invited(int client_fd);
		bool				remove_operator(int client_fd);
		void				remove_member(int client_fd);
		bool				add_operator(int client_fd);
		bool				is_operator(int client_fd) const;
		void				add_invited(int client_fd);
		bool				is_invited(int client_fd) const;
		bool				is_invite_only() const;
		bool				is_topic_restricted() const;
		bool				has_key() const;
		bool				has_user_limit() const;

		void				broadcast(const Wire &message, int except_fd = -1) const;
		void				broadcast(const Client &client, const Wire &cmd, const Wire &param = "") const;
		void				broadcast_from(const Client &client, const Wire &cmd, const Wire &param = "") const;
};

#endif