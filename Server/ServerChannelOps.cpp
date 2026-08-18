#include "Server.hpp"
#include "../Client/Client.hpp"
#include <sys/socket.h>
#include <cstdlib>
#include <string>
#include "../helpers/Wire.hpp"


///////////////////////////////////////////////////////////////////////////////
// OPERATION HELPER

//Function to add modes cleaner. 
static void	append_mode_change(Wire &applied_modes, char sign, char mode)
{
	if (applied_modes.empty() || applied_modes[applied_modes.size() - 1] != sign)
		applied_modes.push_back(sign);
	applied_modes.push_back(mode);
}

//Checks if the channel exists. If not, a error reply is send to the client.
static bool	ensure_channel_exists(Server &server, Client &client,
	const Wire &channel_name, ChannelMap::iterator &channel_it)
{
	channel_it = server.get_channels().find(channel_name);
	if (channel_it == server.get_channels().end())
	{
		server.send_status(client, "403", channel_name + " :No such channel");
		return false;
	}
	return true;
}

//Checks if the client is a channel member. If not, a error reply is send to the client.
static bool	ensure_channel_member(Server &server, Client &client,
	const Wire &channel_name, ChannelMap::iterator &channel_it)
{
	if (!channel_it->second.has_member(client.get_socket()))
	{
		server.send_status(client, "442", channel_name + " :You're not on that channel");
		return false;
	}
	return true;
}

//Checks if the client is a channel operator. If not, a error reply is send to the client.
static bool	ensure_channel_operator(Server &server, Client &client,
	const Wire &channel_name, ChannelMap::iterator &channel_it)
{
	if (!channel_it->second.is_operator(client.get_socket()))
	{
		server.send_status(client, "482", channel_name + " :You're not channel operator");
		return false;
	}
	return true;
}


///////////////////////////////////////////////////////////////////////////////
// KICK

void	Server::handle_kick(Client &client, const Wire &line,
	const Vector<Wire> &arguments)
{
	//First it checks if there are enough arguments.
	if (arguments.size() < 2)
	{
		send_status(client, "461", "KICK :Not enough parameters");
		return ;
	}

	//Sets them to variables for readability.
	const Wire &channel_name = arguments[0];
	const Wire &target_nick = arguments[1];

	//Checks if the channel exists and if the kicking client is a channel member with operator rights.
	ChannelMap::iterator channel_it;
	if (!ensure_channel_exists(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_member(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_operator(*this, client, channel_name, channel_it))
		return ;

	//Checks if the client to kick even exists and is on channel.
	Client *target = find_client_by_nickname(target_nick);
	if (target == NULL)
	{
		send_status(client, "401", target_nick + " :No such nick/channel");
		return ;
	}

	if (!channel_it->second.has_member(target->get_socket()))
	{
		send_status(client, "441", Wire(target_nick, " ", channel_name, " :They aren't on that channel"));
		return ;
	}

	//It provides the reason and the kick message, announces it to the channel and kicks the client.
	Wire reason = client.get_nickname();
	if (line.contains(" :"))
		reason = line.strAfter(" :");

	Wire kick_message = make_msg(client, "KICK", channel_name + " " + target_nick, reason);
	channel_it->second.broadcast(kick_message);
	channel_it->second.remove_member_from_channel(target->get_socket());
	// delete channel if self kick
	if (channel_it->second.get_member_fds().empty())
		get_channels().erase(channel_it);
}


///////////////////////////////////////////////////////////////////////////////
// INVITE

void	Server::handle_invite(Client &client,
	const Vector<Wire> &arguments)
{
	//First it checks if there are enough arguments.
	if (arguments.size() < 2)
	{
		send_status(client, "461", "INVITE :Not enough parameters");
		return ;
	}

	//Sets them to variables for readability.
	const Wire &target_nick = arguments[0];
	const Wire &channel_name = arguments[1];

	//Checks if the channel exists and if the inviting client is a channel member with operator rights.
	ChannelMap::iterator channel_it;
	if (!ensure_channel_exists(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_member(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_operator(*this, client, channel_name, channel_it))
		return ;

	//Checks if the client to invite even exists and is on channel.
	Client *target = find_client_by_nickname(target_nick);
	if (target == NULL)
	{
		send_status(client, "401", target_nick + " :No such nick/channel");
		return ;
	}

	if (channel_it->second.has_member(target->get_socket()))
	{
		send_status(client, "443", Wire(target_nick, " ", channel_name, " :is already on channel"));
		return ;
	}

	//Builds the invite message and reply, then sends it to the clients.
	send_msg(target->get_socket(), client, "INVITE", target_nick, channel_name);
	send_status(client, "341", target_nick + " " + channel_name);

	channel_it->second.add_invited(target->get_socket());
}


///////////////////////////////////////////////////////////////////////////////
// TOPIC

void	Server::handle_topic(Client &client, const Wire &line,
	const Vector<Wire> &arguments)
{
	//First it checks if there are enough arguments.
	if (arguments.size() < 1)
	{
		send_status(client, "461", "TOPIC :Not enough parameters");
		return ;
	}

	//Store the channel name from the command parameters.
	const Wire &channel_name = arguments[0];

	//Checks if the channel exists and if the inviting client is a channel member.
	ChannelMap::iterator channel_it;
	if (!ensure_channel_exists(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_member(*this, client, channel_name, channel_it))
		return ;

	//Look for the topic text after " :".
	//If it is missing, the client is only asking for the current topic.
	if (!line.contains(" :"))
	{
		//Gets the topic of the channel, if it's missing, the client gets messaged else it sends him the topic.
		Wire error_code = channel_it->second.get_topic().empty() ? "331" : "332";
		Wire topic = channel_it->second.get_topic().placeholder("No topic is set");
		send_status(client, error_code, channel_name + " :" + topic);
		return ;
	}

	//If the topic is restricted, only channel operators can change it.
	if (channel_it->second.is_topic_restricted()
		&& !channel_it->second.is_operator(client.get_socket()))
	{
		send_status(client, "482", channel_name + " :You're not channel operator");
		return ;
	}

	//Sets the new topic.
	Wire new_topic = line.strAfter(" :");
	channel_it->second.set_topic(new_topic);

	//Broadcast the topic change to every member of the channel.
	channel_it->second.broadcast(client, "TOPIC", new_topic);
}


///////////////////////////////////////////////////////////////////////////////
// MODE

void	Server::handle_mode(Client &client, const Wire &line,
	const Vector<Wire> &arguments)
{
	(void)line;
	//Check that the args are not empty.
	if (arguments.empty())
	{
		send_status(client, "461", "MODE :Not enough parameters");
		return ;
	}

	//Get the channel name.
	const Wire &channel_name = arguments[0];

	//Only channel names beginning with '#' are valid.
	if (channel_name.empty() || channel_name[0] != '#')
		return ;

	//Ensure the channel exists and the client is part of it.
	ChannelMap::iterator channel_it;
	if (!ensure_channel_exists(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_member(*this, client, channel_name, channel_it))
		return ;

	//If only the channel name was provided, return the current channel modes.
	if (arguments.size() == 1)
	{
		//Collect the active modes and any additional parameters they need.
		Wire current_modes = "+";
		Wire current_params;

		if (channel_it->second.is_invite_only())
			current_modes.push_back('i');
		if (channel_it->second.is_topic_restricted())
			current_modes.push_back('t');
		if (channel_it->second.has_key())
		{
			current_modes.push_back('k');
			current_params += " " + channel_it->second.get_key();
		}
		if (channel_it->second.has_user_limit())
		{
			current_modes.push_back('l');
			current_params += " " + Wire(channel_it->second.get_user_limit());
		}

		//Send the exact MODES the channel has active.
		send_status(client, "324", Wire(channel_name, " ", current_modes, current_params));
		return ;
	}

	//Changing modes requires operator privileges.
	if (!ensure_channel_operator(*this, client, channel_name, channel_it))
		return ;

	//Get the actual mode string something like: "+itk secret" or "-l".
	const Wire &mode_string = arguments[1];
	char sign = 0;
	size_t param_index = 2;
	Wire applied_modes;
	Wire applied_params;

	//Parse the mode string one character at a time.
	for (size_t i = 0; i < mode_string.size(); ++i)
	{
		char mode = mode_string[i];
		if (mode == '+' || mode == '-')
		{
			//Remember whether the following mode changes are adding or removing.
			sign = mode;
			continue ;
		}
		if (sign == 0)
			continue ;

		//Mode 'i': invite-only flag.
		if (mode == 'i')
		{
			channel_it->second.set_invite_only(sign == '+');
			append_mode_change(applied_modes, sign, 'i');
		}
		//Mode 't': topic restriction flag.
		else if (mode == 't')
		{
			channel_it->second.set_topic_restricted(sign == '+');
			append_mode_change(applied_modes, sign, 't');
		}
		//Mode 'k': channel key; requires a parameter when setting and clears it when removing.
		else if (mode == 'k')
		{
			if (sign == '+')
			{
				if (param_index >= arguments.size())
				{
					send_status(client, "461", "MODE :Not enough parameters");
					continue ;
				}
				channel_it->second.set_key(arguments[param_index]);
				append_mode_change(applied_modes, sign, 'k');
				applied_params += " " + arguments[param_index];
				param_index++;
			}
			else
			{
				if (channel_it->second.has_key())
				{
					channel_it->second.clear_key();
					append_mode_change(applied_modes, sign, 'k');
				}
			}
		}
		//Mode 'o': operator assignment; target is a user nick and must be in the channel.
		else if (mode == 'o')
		{
			if (param_index >= arguments.size())
			{
				send_status(client, "461", "MODE :Not enough parameters");
				continue ;
			}

			const Wire &target_nick = arguments[param_index];
			Client *target = find_client_by_nickname(target_nick);
			if (target == NULL)
			{
				send_status(client, "401", target_nick + " :No such nick/channel");
				param_index++;
				continue ;
			}
			if (!channel_it->second.has_member(target->get_socket()))
			{
				send_status(client, "441", target_nick + " " + channel_name
					+ " :They aren't on that channel");
				param_index++;
				continue ;
			}

			if (sign == '+')
				channel_it->second.add_operator(target->get_socket());
			else
				channel_it->second.remove_operator(target->get_socket());

			append_mode_change(applied_modes, sign, 'o');
			applied_params += " " + target_nick;
			param_index++;
		}
		//Mode 'l': user limit; requires a numeric value when setting, and clears the limit when removing.
		else if (mode == 'l')
		{
			if (sign == '+')
			{
				if (param_index >= arguments.size() || !is_positive_number(arguments[param_index]))
				{
					send_status(client, "461", "MODE :Not enough parameters");
					if (param_index < arguments.size())
						param_index++;
					continue ;
				}
				size_t limit_value = static_cast<size_t>(std::atoi(arguments[param_index].c_str()));
				channel_it->second.set_user_limit(limit_value);
				append_mode_change(applied_modes, sign, 'l');
				applied_params += " " + arguments[param_index];
				param_index++;
			}
			else
			{
				if (channel_it->second.has_user_limit())
				{
					channel_it->second.clear_user_limit();
					append_mode_change(applied_modes, sign, 'l');
				}
			}
		}
		//Any other character is unsupported and gets an IRC error reply.
		else
		{
			send_status(client, "472", Wire(mode) + " :is unknown mode char to me");
		}
	}

	//If no valid mode actually changed, do not broadcast anything.
	if (applied_modes.empty())
		return ;

	//Build a single MODE message containing all accepted mode changes and their parameters.
	Wire mode_message = make_msg(client, "MODE", Wire(channel_name, " ", applied_modes, applied_params));
	channel_it->second.broadcast(mode_message);
}