#ifndef CHANNEL_HPP
# define CHANNEL_HPP

#include "Client.hpp"
#include <string>
#include <vector>


class	Channel
{
	private:

		std::string			name;
		std::string			topic;
		std::vector<Client> members;


	public:


		Channel();
		Channel(const std::string &name);
		Channel(const Channel &other);
		Channel &operator=(const Channel &other);
		~Channel();

		// void	kick();
		// void	invite();
		// void	topic();
		// void	mode();


		void				set_name(const std::string &name);
		std::string			get_name() const;

		void				set_topic(const std::string &topic);
		std::string			get_topic() const;

		void				add_member(const Client &client);
		void				remove_member(const Client &client);
		std::vector<Client>	get_members() const;
};

#endif