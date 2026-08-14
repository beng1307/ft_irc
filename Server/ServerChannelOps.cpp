#include "Server.hpp"
#include "../Client/Client.hpp"
#include <sys/socket.h>
#include <cstdlib>
#include <string>


///////////////////////////////////////////////////////////////////////////////
// OPERATION HELPER

static void	append_mode_change(std::string &applied_modes, char sign, char mode)
{
	if (applied_modes.empty() || applied_modes[applied_modes.size() - 1] != sign)
		applied_modes.push_back(sign);
	applied_modes.push_back(mode);
}

static std::string	build_client_prefix(const Client &client)
{
	return ":" + client.get_nickname() + "!" + client.get_username() + "@localhost";
}

static std::string	get_client_nick_or_wildcard(const Client &client)
{
	std::string nick = client.get_nickname();
	if (nick.empty())
		nick = "*";
	return nick;
}

static void	broadcast_to_channel(const Channel &channel, const std::string &message)
{
	std::set<int> member_fds = channel.get_member_fds();
	for (std::set<int>::const_iterator it = member_fds.begin(); it != member_fds.end(); ++it)
		send(*it, message.c_str(), message.size(), 0);
}

static bool	ensure_channel_exists(Server &server, Client &client,
	const std::string &channel_name, ChannelMap::iterator &channel_it)
{
	channel_it = server.get_channels().find(channel_name);
	if (channel_it == server.get_channels().end())
	{
		server.send_error_reply(client, "403", channel_name + " :No such channel");
		return false;
	}
	return true;
}

static bool	ensure_channel_member(Server &server, Client &client,
	const std::string &channel_name, ChannelMap::iterator &channel_it)
{
	if (!channel_it->second.has_member(client.get_socket()))
	{
		server.send_error_reply(client, "442", channel_name + " :You're not on that channel");
		return false;
	}
	return true;
}

static bool	ensure_channel_operator(Server &server, Client &client,
	const std::string &channel_name, ChannelMap::iterator &channel_it)
{
	if (!channel_it->second.is_operator(client.get_socket()))
	{
		server.send_error_reply(client, "482", channel_name + " :You're not channel operator");
		return false;
	}
	return true;
}

static std::string	build_mode_reply(const Client &client, const std::string &channel_name,
	const std::string &current_modes, const std::vector<std::string> &current_params)
{
	std::string mode_reply = ":localhost 324 " + get_client_nick_or_wildcard(client)
		+ " " + channel_name + " " + current_modes;
	for (size_t i = 0; i < current_params.size(); ++i)
		mode_reply += " " + current_params[i];
	mode_reply += "\r\n";
	return mode_reply;
}


///////////////////////////////////////////////////////////////////////////////
// KICK

void	Server::handle_kick(Client &client, const std::string &line,
	const std::vector<std::string> &arguments)
{
	if (arguments.size() < 2)
	{
		send_error_reply(client, "461", "KICK :Not enough parameters");
		return ;
	}

	const std::string &channel_name = arguments[0];
	const std::string &target_nick = arguments[1];

	ChannelMap::iterator channel_it;
	if (!ensure_channel_exists(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_member(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_operator(*this, client, channel_name, channel_it))
		return ;

	Client *target = find_client_by_nickname(target_nick);
	if (target == NULL)
	{
		send_error_reply(client, "401", target_nick + " :No such nick/channel");
		return ;
	}

	if (!channel_it->second.has_member(target->get_socket()))
	{
		send_error_reply(client, "441", target_nick + " " + channel_name
			+ " :They aren't on that channel");
		return ;
	}

	std::string reason = client.get_nickname();
	size_t reason_pos = line.find(" :");
	if (reason_pos != std::string::npos && reason_pos + 2 < line.size())
		reason = line.substr(reason_pos + 2);

	std::string kick_message = build_client_prefix(client) + " KICK " + channel_name
		+ " " + target_nick + " :" + reason + "\r\n";
	broadcast_to_channel(channel_it->second, kick_message);
	channel_it->second.remove_member_from_channel(target->get_socket());
}


///////////////////////////////////////////////////////////////////////////////
// INVITE

void	Server::handle_invite(Client &client,
	const std::vector<std::string> &arguments)
{
	if (arguments.size() < 2)
	{
		send_error_reply(client, "461", "INVITE :Not enough parameters");
		return ;
	}

	const std::string &target_nick = arguments[0];
	const std::string &channel_name = arguments[1];

	ChannelMap::iterator channel_it;
	if (!ensure_channel_exists(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_member(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_operator(*this, client, channel_name, channel_it))
		return ;

	Client *target = find_client_by_nickname(target_nick);
	if (target == NULL)
	{
		send_error_reply(client, "401", target_nick + " :No such nick/channel");
		return ;
	}

	if (channel_it->second.has_member(target->get_socket()))
	{
		send_error_reply(client, "443", target_nick + " " + channel_name
			+ " :is already on channel");
		return ;
	}

	std::string invite_message = build_client_prefix(client) + " INVITE " + target_nick
		+ " :" + channel_name + "\r\n";
	send(target->get_socket(), invite_message.c_str(), invite_message.size(), 0);

	std::string invite_reply = ":localhost 341 " + get_client_nick_or_wildcard(client)
		+ " " + target_nick + " " + channel_name + "\r\n";
	send(client.get_socket(), invite_reply.c_str(), invite_reply.size(), 0);

	channel_it->second.add_invited(target->get_socket());
}


///////////////////////////////////////////////////////////////////////////////
// TOPIC

void	Server::handle_topic(Client &client, const std::string &line,
	const std::vector<std::string> &arguments)
{
	if (arguments.size() < 1)
	{
		send_error_reply(client, "461", "TOPIC :Not enough parameters");
		return ;
	}

	const std::string &channel_name = arguments[0];
	ChannelMap::iterator channel_it;
	if (!ensure_channel_exists(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_member(*this, client, channel_name, channel_it))
		return ;

	size_t topic_pos = line.find(" :");
	if (topic_pos == std::string::npos)
	{
		std::string nick = get_client_nick_or_wildcard(client);
		std::string topic = channel_it->second.get_topic();
		if (topic.empty())
		{
			std::string no_topic_reply = ":localhost 331 " + nick + " "
				+ channel_name + " :No topic is set\r\n";
			send(client.get_socket(), no_topic_reply.c_str(), no_topic_reply.size(), 0);
		}
		else
		{
			std::string topic_reply = ":localhost 332 " + nick + " "
				+ channel_name + " :" + topic + "\r\n";
			send(client.get_socket(), topic_reply.c_str(), topic_reply.size(), 0);
		}
		return ;
	}

	if (channel_it->second.is_topic_restricted()
		&& !channel_it->second.is_operator(client.get_socket()))
	{
		send_error_reply(client, "482", channel_name + " :You're not channel operator");
		return ;
	}

	std::string new_topic = line.substr(topic_pos + 2);
	channel_it->second.set_topic(new_topic);

	std::string topic_message = build_client_prefix(client) + " TOPIC " + channel_name
		+ " :" + new_topic + "\r\n";
	broadcast_to_channel(channel_it->second, topic_message);
}


///////////////////////////////////////////////////////////////////////////////
// MODE

void	Server::handle_mode(Client &client, const std::string &line,
	const std::vector<std::string> &arguments)
{
	(void)line;
	if (arguments.empty())
	{
		send_error_reply(client, "461", "MODE :Not enough parameters");
		return ;
	}

	const std::string &channel_name = arguments[0];

	if (channel_name.empty() || channel_name[0] != '#')
		return ;

	ChannelMap::iterator channel_it;
	if (!ensure_channel_exists(*this, client, channel_name, channel_it))
		return ;
	if (!ensure_channel_member(*this, client, channel_name, channel_it))
		return ;

	if (arguments.size() == 1)
	{
		std::string current_modes = "+";
		std::vector<std::string> current_params;

		if (channel_it->second.is_invite_only())
			current_modes.push_back('i');
		if (channel_it->second.is_topic_restricted())
			current_modes.push_back('t');
		if (channel_it->second.has_key())
		{
			current_modes.push_back('k');
			current_params.push_back(channel_it->second.get_key());
		}
		if (channel_it->second.has_user_limit())
		{
			current_modes.push_back('l');
			current_params.push_back(to_string_size_t(channel_it->second.get_user_limit()));
		}

		std::string mode_reply = build_mode_reply(client, channel_name, current_modes, current_params);
		send(client.get_socket(), mode_reply.c_str(), mode_reply.size(), 0);
		return ;
	}

	if (!ensure_channel_operator(*this, client, channel_name, channel_it))
		return ;

	const std::string &mode_string = arguments[1];
	char sign = 0;
	size_t param_index = 2;
	std::string applied_modes;
	std::vector<std::string> applied_params;

	for (size_t i = 0; i < mode_string.size(); ++i)
	{
		char mode = mode_string[i];
		if (mode == '+' || mode == '-')
		{
			sign = mode;
			continue ;
		}
		if (sign == 0)
			continue ;

		if (mode == 'i')
		{
			channel_it->second.set_invite_only(sign == '+');
			append_mode_change(applied_modes, sign, 'i');
		}
		else if (mode == 't')
		{
			channel_it->second.set_topic_restricted(sign == '+');
			append_mode_change(applied_modes, sign, 't');
		}
		else if (mode == 'k')
		{
			if (sign == '+')
			{
				if (param_index >= arguments.size())
				{
					send_error_reply(client, "461", "MODE :Not enough parameters");
					continue ;
				}
				channel_it->second.set_key(arguments[param_index]);
				append_mode_change(applied_modes, sign, 'k');
				applied_params.push_back(arguments[param_index]);
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
		else if (mode == 'o')
		{
			if (param_index >= arguments.size())
			{
				send_error_reply(client, "461", "MODE :Not enough parameters");
				continue ;
			}

			const std::string &target_nick = arguments[param_index];
			Client *target = find_client_by_nickname(target_nick);
			if (target == NULL)
			{
				send_error_reply(client, "401", target_nick + " :No such nick/channel");
				param_index++;
				continue ;
			}
			if (!channel_it->second.has_member(target->get_socket()))
			{
				send_error_reply(client, "441", target_nick + " " + channel_name
					+ " :They aren't on that channel");
				param_index++;
				continue ;
			}

			if (sign == '+')
				channel_it->second.add_operator(target->get_socket());
			else
				channel_it->second.remove_operator(target->get_socket());

			append_mode_change(applied_modes, sign, 'o');
			applied_params.push_back(target_nick);
			param_index++;
		}
		else if (mode == 'l')
		{
			if (sign == '+')
			{
				if (param_index >= arguments.size() || !is_positive_number(arguments[param_index]))
				{
					send_error_reply(client, "461", "MODE :Not enough parameters");
					if (param_index < arguments.size())
						param_index++;
					continue ;
				}
				size_t limit_value = static_cast<size_t>(std::atoi(arguments[param_index].c_str()));
				channel_it->second.set_user_limit(limit_value);
				append_mode_change(applied_modes, sign, 'l');
				applied_params.push_back(arguments[param_index]);
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
		else
		{
			send_error_reply(client, "472", std::string(1, mode) + " :is unknown mode char to me");
		}
	}

	if (applied_modes.empty())
		return ;

	std::string mode_message = build_client_prefix(client) + " MODE " + channel_name
		+ " " + applied_modes;
	for (size_t i = 0; i < applied_params.size(); ++i)
		mode_message += " " + applied_params[i];
	mode_message += "\r\n";
	broadcast_to_channel(channel_it->second, mode_message);
}