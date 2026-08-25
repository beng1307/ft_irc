#include "Server.hpp"
#include "../Client/Client.hpp"
#include <sys/socket.h>
#include <cstdlib>
#include <string>
#include "../helpers/Wire.hpp"


///////////////////////////////////////////////////////////////////////////////
// OPERATION HELPER

// Appends a mode change to applied_modes, managing signs and deduplicating in the current group.
static void	append_mode_change(Wire &applied_modes, char sign, char mode)
{
	if (applied_modes.find_last_char("+-") != sign)
		applied_modes.push_back(sign);

	size_t last_sign_pos = applied_modes.find_last_of("+-");
	if (applied_modes.find(mode, last_sign_pos) == string::npos)
		applied_modes.push_back(mode);
}

//Checks if the channel exists. If not, a error reply is send to the client.
Channel	&Server::ensure_channel_exists(Client &client,
	const Wire &channel_name)
{
	Channel &channel = get_channel(channel_name);
	if (!channel)
		send_status(client, "403", channel_name + " :No such channel");
	return channel;
}

//Checks if the client is a channel member. If not, a error reply is send to the client.
bool	Server::ensure_channel_member(Client &client,
	Channel &channel)
{
	if (!channel.has_member(client.get_socket()))
	{
		send_status(client, "442", channel.get_name() + " :You're not on that channel");
		return false;
	}
	return true;
}

//Checks if the client is a channel operator. If not, a error reply is send to the client.
bool	Server::ensure_channel_operator(Client &client,
	Channel &channel)
{
	if (!channel.is_operator(client.get_socket()))
	{
		send_status(client, "482", channel.get_name() + " :You're not channel operator");
		return false;
	}
	return true;
}


///////////////////////////////////////////////////////////////////////////////
// KICK

void	Server::handle_kick(Client &client, const Vector<Wire> &arguments)
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
	Channel &channel = ensure_channel_exists(client, channel_name);
	if (!channel)
		return ;
	if (!ensure_channel_member(client, channel))
		return ;
	if (!ensure_channel_operator(client, channel))
		return ;

	//Checks if the client to kick even exists and is on channel.
	Client &target = get_client(target_nick);
	if (!target)
	{
		send_status(client, "401", target_nick + " :No such nick/channel");
		return ;
	}

	if (!channel.has_member(target.get_socket()))
	{
		send_status(client, "441", Wire(target_nick, " ", channel_name, " :They aren't on that channel"));
		return ;
	}

	//It provides the reason and the kick message, announces it to the channel and kicks the client.
	Wire reason = client.get_nickname();
	if (arguments.size() > 2)
		reason = arguments[2];

	Wire kick_message = make_msg(client, "KICK", channel_name + " " + target_nick, reason);
	channel.broadcast(kick_message);
	channel.remove_client_from_channel(target.get_socket());
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
	Channel &channel = ensure_channel_exists(client, channel_name);
	if (!channel)
		return ;
	if (!ensure_channel_member(client, channel))
		return ;
	if (!ensure_channel_operator(client, channel))
		return ;

	//Checks if the client to invite even exists and is on channel.
	Client &target = get_client(target_nick);
	if (!target || !target.get_register_status())
	{
		send_status(client, "401", target_nick + " :No such nick/channel");
		return ;
	}

	if (channel.has_member(target.get_socket()))
	{
		send_status(client, "443", Wire(target_nick, " ", channel_name, " :is already on channel"));
		return ;
	}

	//Builds the invite message and reply, then sends it to the clients.
	target.send(make_msg(client, "INVITE", target_nick, channel_name));
	send_status(client, "341", target_nick + " " + channel_name);

	channel.add_invited(target.get_socket());
}


///////////////////////////////////////////////////////////////////////////////
// TOPIC

void	Server::handle_topic(Client &client, const Vector<Wire> &arguments)
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
	Channel &channel = ensure_channel_exists(client, channel_name);
	if (!channel)
		return ;
	if (!ensure_channel_member(client, channel))
		return ;

	if (arguments.size() < 2)
	{
		//Gets the topic of the channel, if it's missing, the client gets messaged else it sends him the topic.
		Wire error_code = channel.get_topic().empty() ? "331" : "332";
		Wire topic = channel.get_topic().placeholder("No topic is set");
		send_status(client, error_code, channel_name + " :" + topic);
		return ;
	}

	//If the topic is restricted, only channel operators can change it.
	if (channel.is_topic_restricted()
		&& !channel.is_operator(client.get_socket()))
	{
		send_status(client, "482", channel_name + " :You're not channel operator");
		return ;
	}

	//Sets the new topic.
	static const size_t MAX_TOPIC_LENGTH = 150;
	Wire new_topic = arguments[1];
	if (new_topic.length() > MAX_TOPIC_LENGTH)
	{
		send_status(client, "461", "TOPIC :Topic length is too long");
		return ;
	}
	channel.set_topic(new_topic);

	//Broadcast the topic change to every member of the channel.
	channel.broadcast(client, "TOPIC", new_topic);
}


///////////////////////////////////////////////////////////////////////////////
// MODE HELPERS

// Counts parameters required by mode flags in the mode string.
static size_t	count_required_mode_parameters(const Wire &mode_string)
{
	char sign = 0;
	size_t count = 0;
	for (size_t i = 0; i < mode_string.size(); ++i)
	{
		char c = mode_string[i];
		if (Wire("+-").contains(c))
			sign = c;
		else if ((sign == '+' && Wire("klo").contains(c)) || (sign == '-' && c == 'o'))
			count++;
	}
	return count;
}

// Builds and sends the active channel modes (RPL_CHANNELMODEIS 324).
void	Server::send_channel_modes_reply(Client &client, const Channel &channel)
{
	Wire current_modes = "+";
	Wire current_params;

	if (channel.is_invite_only())
		current_modes.push_back('i');
	if (channel.is_topic_restricted())
		current_modes.push_back('t');
	if (channel.has_key())
	{
		current_modes.push_back('k');
		current_params += " " + channel.get_key();
	}
	if (channel.has_user_limit())
	{
		current_modes.push_back('l');
		current_params += " " + Wire(channel.get_user_limit());
	}

	send_status(client, "324", Wire(channel.get_name(), " ", current_modes, current_params));
}

// Applies channel key flag ('k').
bool	Server::apply_mode_key(Client &client, Channel &channel, char sign,
	const Vector<Wire> &arguments, size_t &param_index,
	Wire &applied_modes, Wire &applied_params)
{
	if (sign == '+')
	{
		if (param_index >= arguments.size())
		{
			send_status(client, "461", "MODE :Not enough parameters");
			return (false);
		}
		const Wire &key = arguments[param_index++];
		if (channel.has_key())
		{
			send_status(client, "467", channel.get_name() + " :Channel key already set");
			return (false);
		}
		if (key.is_empty() || key.containsOneOf(" \t\r\n"))
		{
			send_status(client, "525", channel.get_name() + " :Key is not well-formed");
			return (false);
		}
		bool changed = channel.set_key(key);
		append_mode_change(applied_modes, sign, 'k');
		applied_params += " " + key;
		return (changed);
	}
	if (channel.has_key())
	{
		bool changed = channel.clear_key();
		append_mode_change(applied_modes, sign, 'k');
		return (changed);
	}
	return (false);
}

// Applies channel operator flag ('o').
bool	Server::apply_mode_operator(Client &client, Channel &channel, char sign,
	const Vector<Wire> &arguments, size_t &param_index,
	Wire &applied_modes, Wire &applied_params)
{
	if (param_index >= arguments.size())
	{
		send_status(client, "461", "MODE :Not enough parameters");
		return (false);
	}

	const Wire &target_nick = arguments[param_index++];
	Client &target = get_client(target_nick);
	if (!target)
	{
		send_status(client, "401", target_nick + " :No such nick/channel");
		return (false);
	}
	if (!channel.has_member(target.get_socket()))
	{
		send_status(client, "441", Wire(target_nick, " ", channel.get_name(),
			" :They aren't on that channel"));
		return (false);
	}

	bool changed = (sign == '+') ? channel.add_operator(target.get_socket())
		: channel.remove_operator(target.get_socket());
	append_mode_change(applied_modes, sign, 'o');
	applied_params += " " + target_nick;
	return (changed);
}

// Applies channel user limit flag ('l').
bool	Server::apply_mode_limit(Client &client, Channel &channel, char sign,
	const Vector<Wire> &arguments, size_t &param_index,
	Wire &applied_modes, Wire &applied_params)
{
	if (sign == '+')
	{
		if (param_index >= arguments.size() || !is_positive_number(arguments[param_index]))
		{
			send_status(client, "461", "MODE :Not enough parameters");
			return (false);
		}
		const Wire &limit_str = arguments[param_index++];
		size_t limit_value = limit_str.toInt();
		bool changed = channel.set_user_limit(limit_value);
		append_mode_change(applied_modes, sign, 'l');
		applied_params += " " + limit_str;
		return (changed);
	}
	if (channel.has_user_limit())
	{
		bool changed = channel.clear_user_limit();
		append_mode_change(applied_modes, sign, 'l');
		return (changed);
	}
	return (false);
}


///////////////////////////////////////////////////////////////////////////////
// MODE

void	Server::handle_mode(Client &client, const Vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "461", "MODE :Not enough parameters");
		return ;
	}

	const Wire &channel_name = arguments[0];
	if (channel_name.empty() || (channel_name[0] != '#' && channel_name[0] != '&'))
		return ;

	Channel &channel = ensure_channel_exists(client, channel_name);
	if (!channel || !ensure_channel_member(client, channel))
		return ;

	if (arguments.size() == 1)
	{
		send_channel_modes_reply(client, channel);
		return ;
	}

	const Wire &mode_string = arguments[1];
	if (mode_string == "b" || mode_string == "+b")
	{
		send_status(client, "368", channel_name + " :End of Channel Ban List");
		return ;
	}

	if (!ensure_channel_operator(client, channel))
		return ;

	// Reject if parameters are starved for the requested flags
	size_t required_params = count_required_mode_parameters(mode_string);
	if (arguments.size() < 2 + required_params)
	{
		send_status(client, "461", "MODE :Not enough parameters");
		return ;
	}

	bool state_changed = false;
	char sign = 0;
	size_t param_index = 2;
	Wire applied_modes;
	Wire applied_params;

	for (size_t i = 0; i < mode_string.size(); ++i)
	{
		char mode = mode_string[i];
		if (mode == '+' || mode == '-')
		{
			sign = mode;
			continue ;
		}
		if (sign == 0)
		{
			send_status(client, "472", Wire(mode) + " :is unknown mode char to me");
			continue ;
		}

		if (mode == 'i')
		{
			state_changed = channel.set_invite_only(sign == '+') || state_changed;
			append_mode_change(applied_modes, sign, 'i');
		}
		else if (mode == 't')
		{
			state_changed = channel.set_topic_restricted(sign == '+') || state_changed;
			append_mode_change(applied_modes, sign, 't');
		}
		else if (mode == 'k')
		{
			state_changed = apply_mode_key(client, channel, sign, arguments, param_index, applied_modes, applied_params) || state_changed;
		}
		else if (mode == 'o')
		{
			state_changed = apply_mode_operator(client, channel, sign, arguments, param_index, applied_modes, applied_params) || state_changed;
		}
		else if (mode == 'l')
		{
			if (sign == '+' && (param_index >= arguments.size() || !is_positive_number(arguments[param_index])))
			{
				send_status(client, "461", "MODE :Not enough parameters");
				break ;
			}
			state_changed = apply_mode_limit(client, channel, sign, arguments, param_index, applied_modes, applied_params) || state_changed;
		}
		else
		{
			send_status(client, "472", Wire(mode) + " :is unknown mode char to me");
		}
	}

	if (applied_modes.empty() || !state_changed)
		return ;

	Wire mode_message = make_msg(client, "MODE", Wire(channel_name, " ", applied_modes, applied_params));
	channel.broadcast(mode_message);
}