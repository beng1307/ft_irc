#ifndef CLIENT_HPP
# define CLIENT_HPP

#include <string>

class Client
{
	private:
		
		///////////////////////////////////////////////////////////////////////////////
		// Private Variables
		
		int				socket;

		std::string		password;
		std::string		username;
		std::string		nickname;
		
		bool			is_registered;
		bool 			is_admin;

		std::string		buffer;

	public:

		///////////////////////////////////////////////////////////////////////////////
		// Constructors and destructor

		Client();
		Client(int socket);
		Client &operator=(const Client &other);
		Client(const Client &other);

		///////////////////////////////////////////////////////////////////////////////
		// Setter & Getter

		void		set_socket(const int &socket);
		int			get_socket() const;

		void		set_password(const std::string &password);
		std::string	get_password() const;

		void		set_username(const std::string &username);
		std::string	get_username() const;

		void		set_nickname(const std::string &nickname);
		std::string	get_nickname() const;

		void		set_admin_status(const bool &admin_status);
		bool		get_admin_status() const;

		void		set_register_status(const bool &register_status);
		bool		get_register_status() const;

		void		set_buffer(const std::string &nickname);
		std::string	get_buffer() const;

};
		

#endif