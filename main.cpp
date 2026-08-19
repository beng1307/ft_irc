#include "Server/Server.hpp"
#include "Channel/Channel.hpp"
#include "Client/Client.hpp"
#include <iostream>
#include <string>
#include <cstdlib>
#include <csignal>
#include "helpers/print.hpp"
#include "helpers/Wire.hpp"

// Global execution flag shared with ServerLoop.cpp.
// When a termination signal (SIGINT / SIGTERM) is caught by sig_handler,
// this flag is cleared to false so the main event loop in server_loop()
// terminates cleanly and executes resource teardown instead of an abrupt abort.
bool g_running = true;

// Signal handler for SIGINT (Ctrl+C) and SIGTERM (kill).
// Rationale: Rather than letting the OS kill the process immediately,
// intercepting these signals allows poll() to unblock via EINTR and allows
// the server loop to cleanly close all active client FDs and release the listening socket.
static void sig_handler(int sig)
{
	(void)sig;
	g_running = false;
}

// Validates the CLI port string parameter.
// Scenarios handled:
//  - Non-numeric inputs (e.g. "abc", "6667abc"): rejected before atoi/strtol.
//  - Negative values (e.g. "-1", "-6667"): prevents underflow/wrapping into invalid unsigned values.
//  - Port zero ("0"): prevents binding to port 0 (which triggers OS dynamic ephemeral port assignment).
//  - Out-of-range ports (> 65535): prevents 16-bit unsigned integer overflow in sockaddr_in.sin_port.
// Returns true only if the string consists purely of digits and evaluates to [1, 65535].
static bool is_valid_port(const char *str, unsigned int &port)
{
	if (!str || !*str)
		return false;
	for (size_t i = 0; str[i]; ++i)
	{
		if (str[i] < '0' || str[i] > '9')
			return false;
	}
	long val = std::strtol(str, NULL, 10);
	if (val <= 0 || val > 65535)
		return false;
	port = static_cast<unsigned int>(val);
	return true;
}

int main(int ac, char **av)
{
	// CLI Argument count check:
	// syntax: ./ircserv <port> <password>
	// If 0, 1, or >2 arguments are given, report usage to stderr and exit with non-zero code.
	if (ac != 3)
	{
		printErr("Usage: ./ircserv <port> <password>");
		return (1);
	}

	// CLI Port validation:
	// Ensures port is a valid numeric TCP port in the valid range [1..65535].
	// Fails fast with non-zero exit code if invalid.
	unsigned int port = 0;
	if (!is_valid_port(av[1], port))
	{
		printErr("Error: Invalid port number: ", av[1]);
		return (1);
	}

	// CLI Password validation:
	// Disallows empty password string to ensure server cannot be launched unauthenticated.
	Wire password(av[2]);
	if (password.empty())
	{
		printErr("Error: Password cannot be empty.");
		return (1);
	}

	// Signal registration:
	// Register handlers for clean graceful teardown on SIGINT (Ctrl+C) and SIGTERM.
	std::signal(SIGINT, sig_handler);
	std::signal(SIGTERM, sig_handler);

	Server server(port, password);

	// Socket initialization & bind check:
	// Scenarios handled:
	//  - Privileged ports (<1024 without root privileges): bind() returns EACCES.
	//  - Port collision (EADDRINUSE): another instance or daemon is already listening on this port.
	//  - Socket creation failures.
	// Rationale: If socket_setup() fails, we must exit immediately with code 1.
	// Otherwise, calling server_loop() on an uninitialized/unbound socket causes poll() to hang forever.
	if (server.socket_setup() != 0)
		return (1);

	// Enter the non-blocking polling event loop
	server.server_loop();

	return (0);
}