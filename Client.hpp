#ifndef CLIENT_HPP
# define CLIENT_HPP

#include <string>

class Client
{
	public:

		///////////////////////////////////////////////////////////////////////////////
		// Public Constructors and destructor

		Client();
		Client(int socket);
		Client &operator=(const Client &other);
		Client(const Client &other);

		///////////////////////////////////////////////////////////////////////////////
		// Public Variables

		int				socket;
		std::string		nickname;
		std::string		username;
		std::string		realname;

		bool			is_registered;
		bool 			is_admin;

		std::string		buffer;

		///////////////////////////////////////////////////////////////////////////////
		// Public Methods

};

#endif