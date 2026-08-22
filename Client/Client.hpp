#ifndef CLIENT_HPP
# define CLIENT_HPP

#include "../helpers/Wire.hpp"


class Server;

class Client
{
	private:
		
		///////////////////////////////////////////////////////////////////////////////
		// Private Variables
		
		Server			*server;
		int				socket;

		Wire			password;
		Wire			username;
		Wire			nickname;
		
		bool			pass_ok;
		bool			is_registered;
		bool 			is_admin;
		bool			close_after_output;

		Wire			buffer;
		Wire			out_buffer;

	public:

		OK_CHECK(Client);

		///////////////////////////////////////////////////////////////////////////////
		// Constructors and destructor

		Client();
		Client(int socket, Server *server = NULL);
		Client &operator=(const Client &other);
		Client(const Client &other);

		
		///////////////////////////////////////////////////////////////////////////////
		// Methods & helper functions
		
		void register_client(const Wire &password);
		void send(Wire message = Wire());


		///////////////////////////////////////////////////////////////////////////////
		// Setter & Getter

		void		set_server(Server *server);
		Server		*get_server() const;

		void		set_socket(const int &socket);
		int			get_socket() const;

		void		set_password(const Wire &password);
		Wire		get_password() const;

		void		set_pass_ok(const bool &pass_ok);
		bool		get_pass_ok() const;

		void		set_username(const Wire &username);
		Wire		get_username() const;

		void		set_nickname(const Wire &nickname);
		Wire		get_nickname() const;

		void		set_admin_status(const bool &admin_status);
		bool		get_admin_status() const;

		void		set_register_status(const bool &register_status);
		bool		get_register_status() const;

		void		set_buffer(const Wire &buffer);
		Wire		&get_buffer();
		Wire		get_buffer() const;
		void		append_raw_buffer(const char *data, size_t size);
		void		append_buffer(const Wire &data);

		void		set_out_buffer(const Wire &out_buffer);
		Wire		&get_out_buffer();
		Wire		get_out_buffer() const;
		void		set_close_after_output(bool close_after_output);
		bool		get_close_after_output() const;

};
		

#endif