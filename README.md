*This project has been created as part of the 42 curriculum by beng1307, tbatis.*

# ft_irc

## Description

`ft_irc` is a C++98 implementation of a small Internet Relay Chat (IRC) server. Its goal is to provide the core IRC workflow over TCP/IP while handling multiple clients through a single non-blocking `poll()` event loop.

Clients authenticate with a password, choose a nickname and username, join channels, and exchange private or channel messages. The server also implements channel operators and the required operator commands: `KICK`, `INVITE`, `TOPIC`, and `MODE` (`i`, `t`, `k`, `o`, and `l`).

The project does not implement an IRC client or server-to-server communication.

## Features

- Non-blocking sockets managed by `poll()`
- Password-based registration with `PASS`, `NICK`, and `USER`
- Channel creation, joining, leaving, and membership broadcasts
- Private messages and channel messages with `PRIVMSG`
- Channel topics, invitations, keys, user limits, and operator privileges
- IRC keepalive support through `PING` / `PONG`
- Connection cleanup after `QUIT`, peer disconnects, and socket errors

## Instructions

### Prerequisites

- A C++ compiler with C++98 support
- GNU Make
- A POSIX-compatible system with TCP/IP sockets and `poll()`

Optional:

- [Irssi](https://irssi.org/) for interactive IRC use
- Python 3 for the memory-resilience probe

### Build

```bash
make
```

This builds the `ircserv` executable.

### Run

```bash
./ircserv <port> <password>
```

Example:

```bash
./ircserv 6667 1234
```

The Makefile also provides a shortcut with default values (`6667` and `1234`) or values stored in `.env`:

```bash
make run
make run 6667 mypassword
```

To persist local defaults:

```bash
make env 6667 mypassword
```

### Connect with an IRC client

For example, with Irssi:

```bash
irssi -c localhost -p 6667 -w 1234
```

Then register and join a channel:

```text
/NICK alice
/USER alice 0 * :Alice
/JOIN #general
```

### Connect manually with Netcat (`nc`)

Connect using `nc` (using `-C` for CRLF line endings):

```bash
nc -C 127.0.0.1 6667
```

Then authenticate, register, join a channel, and send messages:

```text
PASS 1234
NICK alice
USER alice 0 * :Alice
JOIN #general
PRIVMSG #general :Hello world!
```


## Project Layout

```text
Channel/     Channel state, membership, operators, and modes
Client/      Per-client registration state and input buffering
Server/      Socket setup, event loop, commands, and message routing
helpers/     Project utility containers and string helpers
```

## Resources

- [RFC 1459 - Internet Relay Chat Protocol](https://www.rfc-editor.org/rfc/rfc1459)
- [RFC 2812 - Internet Relay Chat: Client Protocol](https://www.rfc-editor.org/rfc/rfc2812)
- [Beej's Guide to Network Programming](https://beej.us/guide/bgnet/)
- [`poll(2)` Linux manual page](https://man7.org/linux/man-pages/man2/poll.2.html)
- [Irssi documentation](https://irssi.org/documentation/)

### Use of AI

AI was used in multiple ways: from introducing the subject and the general behavior of an IRC server to explaining technical details like TCP and Sockets and how to use them using C++. Further we created a flexible IRC Client scripting language which allowed us to instantiate seperate clients and run sequences of commands from each - thanks to this scripting ability we created a set of over 400 different scenarios testing the interaction of different clients, commands and states. Ai was also used as a development aid for reviewing edge cases, improving documentation wording, and discussing protocol and socket-handling tradeoffs. All generated suggestions were reviewed, adapted, and validated by the project authors. Most importantly after learning about a feature, task or bug we personally designed the implementation and architecture details, ensuring decisions about design, architecture and implementation remained that of the authors.
