#ifndef CHANNEL_HPP
# define CHANNEL_HPP

#include "../Client/Client.hpp"
#include "../helpers/Wire.hpp"
#include <string>
#include <vector>
#include <set>


class	Channel
{
	private:

///////////////////////////////////////////////////////////////////////////////
// Variables

		Wire				name;
		Wire				topic;

		std::set<int> 		member_fds;
		std::set<int> 		operator_fds;
		std::set<int> 		invited_fds;

		bool				invite_only;
		bool				topic_restricted;

		bool				key_enabled;
		Wire				channel_key;
		bool				limit_enabled;
		size_t				user_limit;


	public:

///////////////////////////////////////////////////////////////////////////////
// Consturctors and destructor

		Channel();
		Channel(const Wire &name);
		Channel(const Channel &other);
		Channel &operator=(const Channel &other);
		~Channel();


///////////////////////////////////////////////////////////////////////////////
// Setter, Getter & Helper

		void				set_name(const Wire &name);
		Wire				get_name() const;

		void				set_topic(const Wire &topic);
		Wire				get_topic() const;
		
		void				set_key(const Wire &key);
		Wire				get_key() const;

		void				set_user_limit(size_t limit);
		size_t				get_user_limit() const;
		
		std::set<int>		get_member_fds() const;

		void				set_invite_only(bool enabled);

		void				add_member(int client_fd);
		bool				has_member(int client_fd) const;
		void				remove_member_from_channel(int client_fd);
		void				remove_invited(int client_fd);
		void				remove_operator(int client_fd);
		void				remove_member(int client_fd);
		void				add_operator(int client_fd);
		bool				is_operator(int client_fd) const;
		void				add_invited(int client_fd);
		bool				is_invited(int client_fd) const;
		bool				is_invite_only() const;
		void				set_topic_restricted(bool enabled);
		bool				is_topic_restricted() const;
		void				clear_key();
		bool				has_key() const;
		void				clear_user_limit();
		bool				has_user_limit() const;
};

#endif