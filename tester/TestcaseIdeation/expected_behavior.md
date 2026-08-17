# Final Expected Behaviors Specification (ft_irc)

This document itemizes every testable behavioral requirement derived from the intersection of RFC 1459/2812 and the project specifications ([req.txt](file:///home/tbatis/core/berg/DOCS/req.txt), [subject.txt](file:///home/tbatis/core/berg/DOCS/subject.txt), [eval.txt](file:///home/tbatis/core/berg/DOCS/eval.txt)).

Each behavior has a unique identifier for direct test-case mapping.

---

## Category 1: Network, Framing & Multiplexing Core (NET)

| ID | Behavior Description | Expected Result / Output |
| :--- | :--- | :--- |
| **NET-01** | **Standard Line Termination (CRLF)** | Server accepts commands terminated by `\r\n` and executes them immediately. |
| **NET-02** | **Unix Line Termination (LF)** | Server accepts commands terminated by single `\n` robustly (essential for `nc` compatibility). |
| **NET-03** | **TCP Packet Fragmentation (Split Chunks)** | Server buffers partial incoming byte streams across multiple `read()`/`recv()` calls (e.g. `PA` $\to$ `SS` $\to$ ` pw\r\n`) and executes only upon delimiter. |
| **NET-04** | **Concatenated Commands (Pipelining)** | Server receives multiple commands in a single TCP read buffer (e.g. `PASS p\r\nNICK n\r\nUSER u 0 * :r\r\n`) and executes them sequentially. |
| **NET-05** | **Empty Lines & Whitespace Resilience** | Server ignores empty lines (`\r\n\r\n`), leading spaces, and trailing whitespace without error or state corruption. |
| **NET-06** | **Command Line Length Limits (512-byte)** | Server handles commands up to 512 bytes; silently truncates or handles gracefully lines exceeding standard IRC buffer limits without buffer overflow. |
| **NET-07** | **Concurrent Non-Blocking Multiplexing** | Server handles at least 10+ simultaneous client sockets on a single `poll()` loop without any client blocking another. |
| **NET-08** | **Client Abrupt Disconnect (TCP FIN/RST)** | When a client socket closes abruptly (without `QUIT`), the server cleans up the descriptor, removes the user from all channels, and informs peers without hanging. |
| **NET-09** | **Disconnect During Partial Command** | If a client sends half a command and disconnects, server cleans up buffer without crashing or corrupting subsequent connections on that recycled fd. |
| **NET-10** | **Suspended Client (`SIGSTOP` / `^Z`) & Channel Flood** | A paused client on a channel must not cause the server event loop to hang when other clients flood messages. Resuming client (`SIGCONT`) receives buffered data cleanly. |

---

## Category 2: Connection Registration & Authentication (AUTH)

| ID | Behavior Description | Expected Result / Output |
| :--- | :--- | :--- |
| **AUTH-01** | **Standard Registration Flow (`PASS` $\to$ `NICK` $\to$ `USER`)** | Upon valid `PASS <correct_pass>`, `NICK <nick>`, and `USER <user> 0 * :<real>`, server replies with `001 RPL_WELCOME`, `002`, `003`, `004`. |
| **AUTH-02** | **Permuted Registration Flow (`PASS` $\to$ `USER` $\to$ `NICK`)** | Registration succeeds and triggers `001 RPL_WELCOME` regardless of whether `NICK` or `USER` is sent second. |
| **AUTH-03** | **Incorrect Server Password** | Sending invalid password on `PASS` results in `464 ERR_PASSWDMISMATCH` and blocks registration. |
| **AUTH-04** | **Duplicate `PASS` After Registration** | Sending `PASS` after registration is complete returns `462 ERR_ALREADYREGISTRED`. |
| **AUTH-05** | **Command Gating (Pre-Registration Rejection)** | Sending commands like `JOIN`, `PRIVMSG`, `MODE`, `TOPIC` prior to completing registration returns `451 ERR_NOTREGISTERED`. |
| **AUTH-06** | **`NICK` Parameter Missing** | Sending `NICK` with no argument returns `431 ERR_NONICKNAMEGIVEN`. |
| **AUTH-07** | **`NICK` Erroneous Characters** | Sending `NICK` starting with digits, spaces, or invalid symbols returns `432 ERR_ERRONEUSNICKNAME`. |
| **AUTH-08** | **`NICK` Collision During Registration** | Requesting a nickname already held by an active user returns `433 ERR_NICKNAMEINUSE`. Client remains unregistered until a valid unique nick is provided. |
| **AUTH-09** | **Dynamic `NICK` Change Post-Registration** | Registered user sending `NICK <newnick>` receives broadcast `:oldnick!user@host NICK :newnick` (also broadcast to all shared channel members), updating server lookup state. |
| **AUTH-10** | **Dynamic `NICK` Change to Occupied Nick** | Registered user sending `NICK` to an existing nick receives `433 ERR_NICKNAMEINUSE`; original nickname remains active and intact. |
| **AUTH-11** | **`USER` Parameter Count Validation** | Sending `USER` with fewer than 4 arguments returns `461 ERR_NEEDMOREPARAMS`. |
| **AUTH-12** | **Duplicate `USER` Post-Registration** | Sending `USER` after already registered returns `462 ERR_ALREADYREGISTRED`. |
| **AUTH-13** | **IRCv3 Capability Negotiation (`CAP LS` / `CAP END`)** | Server handles `CAP LS` (replying with `CAP * LS :` or empty capabilities) and `CAP END`, completing registration cleanly for modern IRC clients. |

---

## Category 3: Keepalive & Connection Lifecycle (LIFE)

| ID | Behavior Description | Expected Result / Output |
| :--- | :--- | :--- |
| **LIFE-01** | **`PING` with Token** | Client sends `PING <token>`; server replies with `:<servername> PONG <servername> :<token>`. |
| **LIFE-02** | **`PING` with Trailing Token** | Client sends `PING :<token>`; server replies with `:<servername> PONG <servername> :<token>`. |
| **LIFE-03** | **`PING` Without Token** | Client sends `PING`; server replies with `409 ERR_NOORIGIN` or `461 ERR_NEEDMOREPARAMS` or echoes default host. |
| **LIFE-04** | **`QUIT` with Custom Reason** | Client sends `QUIT :Leaving for lunch`; server broadcasts `:nick!user@host QUIT :Leaving for lunch` to all peers in shared channels and closes connection. |
| **LIFE-05** | **`QUIT` Without Parameters** | Client sends `QUIT`; server broadcasts default `:nick!user@host QUIT :Client Quit` (or `:nick`) and closes connection cleanly. |
| **LIFE-06** | **`QUIT` Frees Resources & Nickname** | After `QUIT`, user is removed from all channels; their nickname is immediately available for a new client to claim. |
| **LIFE-07** | **`QUIT` Prior to Registration** | Unregistered client sending `QUIT` closes socket immediately without crashing or generating spurious channel broadcasts. |

---

## Category 4: Channel Membership & Navigation (CHAN)

| ID | Behavior Description | Expected Result / Output |
| :--- | :--- | :--- |
| **CHAN-01** | **`JOIN` Nonexistent Channel (Creation & Operator Grant)** | Joining a new `#channel` creates it; sender becomes Channel Operator (`@`). Server sends `JOIN`, `353 RPL_NAMREPLY` (`@<nick>`), `366 RPL_ENDOFNAMES`, and `331 RPL_NOTOPIC`. |
| **CHAN-02** | **`JOIN` Existing Channel (Regular Member)** | Subsequent users joining receive `JOIN` broadcast, `353 RPL_NAMREPLY` (with `@` for op, regular for others), and current `332 RPL_TOPIC` (if set). Existing members receive `:newnick!user@host JOIN :#channel`. |
| **CHAN-03** | **`JOIN` Self-Broadcast Delivery** | The joining client itself receives its own `:nick!user@host JOIN :#channel` before name replies. |
| **CHAN-04** | **`JOIN` Invalid Channel Name Syntax** | `JOIN` without leading `#` or `&` or containing illegal characters returns `403 ERR_NOSUCHCHANNEL` or `476 ERR_BADCHANMASK`. |
| **CHAN-05** | **`JOIN` Missing Parameters** | `JOIN` with no argument returns `461 ERR_NEEDMOREPARAMS`. |
| **CHAN-06** | **`JOIN` Already Joined Channel** | `JOIN` on a channel the user is already in is either ignored or updates state without duplicating member in list. |
| **CHAN-07** | **`PART` Standard Leave with Reason** | `PART #channel :Goodbye` removes user from channel and broadcasts `:nick!user@host PART #channel :Goodbye` to all channel members (including parting user). |
| **CHAN-08** | **`PART` Standard Leave Without Reason** | `PART #channel` broadcasts `:nick!user@host PART #channel` to members. |
| **CHAN-09** | **`PART` Channel Deletion on Last User** | When the final member parts `#channel`, the channel is destroyed; subsequent `JOIN #channel` re-creates it with fresh operator status. |
| **CHAN-10** | **`PART` User Not on Channel** | `PART #channel` when sender is not a member returns `442 ERR_NOTONCHANNEL`. |
| **CHAN-11** | **`PART` Nonexistent Channel** | `PART #fakechan` returns `403 ERR_NOSUCHCHANNEL`. |
| **CHAN-12** | **`PART` Missing Parameters** | `PART` with no arguments returns `461 ERR_NEEDMOREPARAMS`. |

---

## Category 5: Messaging & Communication (MSG)

| ID | Behavior Description | Expected Result / Output |
| :--- | :--- | :--- |
| **MSG-01** | **Channel Broadcast (`PRIVMSG #channel :text`)** | Message is relayed as `:sender!user@host PRIVMSG #channel :text` to every member in `#channel`. |
| **MSG-02** | **Channel Broadcast Sender Isolation** | The sending client MUST NOT receive an echo of its own `PRIVMSG` on the channel. |
| **MSG-03** | **Direct Private Message (`PRIVMSG <nick> :text`)** | Message is relayed as `:sender!user@host PRIVMSG <nick> :text` strictly and exclusively to `<nick>`. No other clients receive it. |
| **MSG-04** | **`PRIVMSG` Missing Recipient Parameter** | `PRIVMSG` with no targets returns `411 ERR_NORECIPIENT`. |
| **MSG-05** | **`PRIVMSG` Missing Text Parameter** | `PRIVMSG <target>` without trailing text or empty message returns `412 ERR_NOTEXTTOSEND`. |
| **MSG-06** | **`PRIVMSG` to Nonexistent Nick** | `PRIVMSG <unknown>` returns `401 ERR_NOSUCHNICK`. |
| **MSG-07** | **`PRIVMSG` to Nonexistent Channel** | `PRIVMSG #unknown :msg` returns `401 ERR_NOSUCHNICK` or `403 ERR_NOSUCHCHANNEL`. |
| **MSG-08** | **`PRIVMSG` Preservation of Spaces & Colons** | Message payload containing colons, spaces, and formatting characters (e.g. `PRIVMSG #c ::hello :world: `) is delivered verbatim in trailing parameter. |

---

## Category 6: Topic Management (TOPIC)

| ID | Behavior Description | Expected Result / Output |
| :--- | :--- | :--- |
| **TOPIC-01** | **`TOPIC` Query When Unset** | `TOPIC #channel` returns `331 RPL_NOTOPIC <nick> #channel :No topic is set`. |
| **TOPIC-02** | **`TOPIC` Query When Set** | `TOPIC #channel` returns `332 RPL_TOPIC <nick> #channel :<topic>`. |
| **TOPIC-03** | **`TOPIC` Modification by Operator** | Channel op sending `TOPIC #channel :New Topic` changes topic and broadcasts `:nick!user@host TOPIC #channel :New Topic` to all members. |
| **TOPIC-04** | **`TOPIC` Modification by Non-Op with `+t` (Denied)** | When mode `+t` is active, non-op sending `TOPIC #channel :text` returns `482 ERR_CHANOPRIVSNEEDED`; topic is unchanged. |
| **TOPIC-05** | **`TOPIC` Modification by Non-Op with `-t` (Allowed)** | When mode `-t` is active, non-op sending `TOPIC #channel :text` succeeds and broadcasts new topic to all members. |
| **TOPIC-06** | **`TOPIC` Clear / Unset** | Sending `TOPIC #channel :` (empty trailing) clears topic; subsequent queries return `331 RPL_NOTOPIC`. |
| **TOPIC-07** | **`TOPIC` Sender Not on Channel** | Sending `TOPIC #channel` when not a member returns `442 ERR_NOTONCHANNEL`. |
| **TOPIC-08** | **`TOPIC` Nonexistent Channel** | Sending `TOPIC #fake` returns `403 ERR_NOSUCHCHANNEL`. |

---

## Category 7: Channel Operator Commands: `KICK` & `INVITE` (OPCMD)

| ID | Behavior Description | Expected Result / Output |
| :--- | :--- | :--- |
| **OPCMD-01** | **`KICK` by Operator with Reason** | Channel op sending `KICK #channel <target> :Rule violation` removes `<target>`, broadcasts `:op!user@host KICK #channel <target> :Rule violation` to all members (including target). Target cannot send to channel anymore. |
| **OPCMD-02** | **`KICK` by Operator without Reason** | `KICK #channel <target>` broadcasts default kick reason (e.g. `:op!user@host KICK #channel <target> :<target>` or `:op`). |
| **OPCMD-03** | **`KICK` Attempt by Non-Operator** | Non-op sending `KICK #channel <target>` returns `482 ERR_CHANOPRIVSNEEDED`; target remains in channel. |
| **OPCMD-04** | **`KICK` Target Not in Channel** | Op sending `KICK #channel <nonmember>` returns `441 ERR_USERNOTINCHANNEL`. |
| **OPCMD-05** | **`KICK` Sender Not in Channel** | Sending `KICK #channel <target>` when sender is not in channel returns `442 ERR_NOTONCHANNEL`. |
| **OPCMD-06** | **`KICK` Nonexistent Channel** | Sending `KICK #fake <target>` returns `403 ERR_NOSUCHCHANNEL`. |
| **OPCMD-07** | **`KICK` Missing Parameters** | `KICK` with insufficient parameters returns `461 ERR_NEEDMOREPARAMS`. |
| **OPCMD-08** | **`INVITE` Standard Operation** | Inviting non-member to channel sends `341 RPL_INVITING <sender> <target> #channel` to sender, and `:sender!user@host INVITE <target> :#channel` to target. |
| **OPCMD-09** | **`INVITE` on `+i` Channel by Operator** | Op invites target; target is added to invite list, allowing target to bypass `+i` on subsequent `JOIN #channel`. |
| **OPCMD-10** | **`INVITE` on `+i` Channel by Non-Operator** | Non-op attempting `INVITE` on `+i` channel returns `482 ERR_CHANOPRIVSNEEDED`. |
| **OPCMD-11** | **`INVITE` User Already in Channel** | Inviting existing member returns `443 ERR_USERONCHANNEL`. |
| **OPCMD-12** | **`INVITE` Nonexistent User** | Inviting non-existent nickname returns `401 ERR_NOSUCHNICK`. |
| **OPCMD-13** | **`INVITE` Sender Not in Channel** | Inviting to a channel sender is not in returns `442 ERR_NOTONCHANNEL`. |

---

## Category 8: Channel Modes (MODE)

| ID | Behavior Description | Expected Result / Output |
| :--- | :--- | :--- |
| **MODE-01** | **Query Channel Modes** | `MODE #channel` returns `324 RPL_CHANNELMODEIS <nick> #channel <modes> [<modeparams>]`. |
| **MODE-02** | **Mode Modification Non-Operator Rejection** | Non-op attempting any `MODE #channel +...` returns `482 ERR_CHANOPRIVSNEEDED`. |
| **MODE-03** | **Mode `+i` (Invite-Only Set)** | Op sends `MODE #channel +i`; broadcasts mode change. Non-invited users joining get `473 ERR_INVITEONLYCHAN`. |
| **MODE-04** | **Mode `-i` (Invite-Only Remove)** | Op sends `MODE #channel -i`; broadcasts mode change. Any user can join without invitation. |
| **MODE-05** | **Mode `+t` (Topic Restriction Set)** | Op sends `MODE #channel +t`; restricts topic edits to ops. |
| **MODE-06** | **Mode `-t` (Topic Restriction Remove)** | Op sends `MODE #channel -t`; allows regular users to edit topic. |
| **MODE-07** | **Mode `+k` (Set Channel Key/Password)** | Op sends `MODE #channel +k <key>`; sets key. Subsequent `JOIN #channel` without key or with wrong key returns `475 ERR_BADCHANNELKEY`. `JOIN #channel <key>` succeeds. |
| **MODE-08** | **Mode `-k` (Remove Channel Key)** | Op sends `MODE #channel -k [<key>]`; clears key. Users can now join without providing a key. |
| **MODE-09** | **Mode `+o` (Grant Channel Operator)** | Op sends `MODE #channel +o <target>`; grants `@` op status, broadcasts `:sender MODE #channel +o <target>` to all members. Target gains op capabilities. |
| **MODE-10** | **Mode `-o` (Revoke Channel Operator)** | Op sends `MODE #channel -o <target>`; revokes op status, broadcasts mode change. Target loses op capabilities. |
| **MODE-11** | **Mode `+o` / `-o` on Non-Member** | `MODE #channel +o <nonmember>` returns `441 ERR_USERNOTINCHANNEL` or `401 ERR_NOSUCHNICK`. |
| **MODE-12** | **Mode `+l` (Set User Limit)** | Op sends `MODE #channel +l <limit>`; sets cap. When member count reaches `<limit>`, new `JOIN` attempts return `471 ERR_CHANNELISFULL`. |
| **MODE-13** | **Mode `-l` (Remove User Limit)** | Op sends `MODE #channel -l`; removes cap. New users can join freely. |
| **MODE-14** | **Mode `+l` Invalid / Non-Numeric Value** | `MODE #channel +l -5` or `MODE #channel +l abc` handles error gracefully without server crash. |
| **MODE-15** | **Multi-Mode / Chained Mode Flags** | Op sends `MODE #channel +itk key`; applies `+i`, `+t`, and `+k key` atomically and broadcasts combined mode string. |
| **MODE-16** | **Unknown Mode Flag** | Op sends `MODE #channel +z`; returns `472 ERR_UNKNOWNMODE` or ignores invalid flag gracefully. |

---

## Category 9: Numerical Replies & Error Formats (NUM)

| ID | Numeric / Error Code | Description / Format Verification |
| :--- | :--- | :--- |
| **NUM-01** | `001 RPL_WELCOME` | `:<server> 001 <nick> :Welcome to the Internet Relay Network <nick>!<user>@<host>` |
| **NUM-02** | `002 RPL_YOURHOST` | `:<server> 002 <nick> :Your host is <server>, running version <ver>` |
| **NUM-03** | `003 RPL_CREATED` | `:<server> 003 <nick> :This server was created <date>` |
| **NUM-04** | `004 RPL_MYINFO` | `:<server> 004 <nick> <server> <ver> <user_modes> <chan_modes>` |
| **NUM-05** | `324 RPL_CHANNELMODEIS` | `:<server> 324 <nick> <channel> <modes> [<modeparams>]` |
| **NUM-06** | `331 RPL_NOTOPIC` | `:<server> 331 <nick> <channel> :No topic is set` |
| **NUM-07** | `332 RPL_TOPIC` | `:<server> 332 <nick> <channel> :<topic>` |
| **NUM-08** | `341 RPL_INVITING` | `:<server> 341 <nick> <target> <channel>` |
| **NUM-09** | `353 RPL_NAMREPLY` | `:<server> 353 <nick> = <channel> :[@]<nick1> [<nick2>]` |
| **NUM-10** | `366 RPL_ENDOFNAMES` | `:<server> 366 <nick> <channel> :End of /NAMES list` |
| **NUM-11** | `401 ERR_NOSUCHNICK` | `:<server> 401 <nick> <target> :No such nick/channel` |
| **NUM-12** | `403 ERR_NOSUCHCHANNEL` | `:<server> 403 <nick> <channel> :No such channel` |
| **NUM-13** | `411 ERR_NORECIPIENT` | `:<server> 411 <nick> :No recipient given (<command>)` |
| **NUM-14** | `412 ERR_NOTEXTTOSEND` | `:<server> 412 <nick> :No text to send` |
| **NUM-15** | `431 ERR_NONICKNAMEGIVEN` | `:<server> 431 <nick> :No nickname given` |
| **NUM-16** | `432 ERR_ERRONEUSNICKNAME` | `:<server> 432 <nick> <badnick> :Erroneous nickname` |
| **NUM-17** | `433 ERR_NICKNAMEINUSE` | `:<server> 433 <nick> <taken_nick> :Nickname is already in use` |
| **NUM-18** | `441 ERR_USERNOTINCHANNEL` | `:<server> 441 <nick> <target> <channel> :They aren't on that channel` |
| **NUM-19** | `442 ERR_NOTONCHANNEL` | `:<server> 442 <nick> <channel> :You're not on that channel` |
| **NUM-20** | `443 ERR_USERONCHANNEL` | `:<server> 443 <nick> <target> <channel> :is already on channel` |
| **NUM-21** | `451 ERR_NOTREGISTERED` | `:<server> 451 <nick> :You have not registered` |
| **NUM-22** | `461 ERR_NEEDMOREPARAMS` | `:<server> 461 <nick> <command> :Not enough parameters` |
| **NUM-23** | `462 ERR_ALREADYREGISTRED` | `:<server> 462 <nick> :Unauthorized command (already registered)` |
| **NUM-24** | `464 ERR_PASSWDMISMATCH` | `:<server> 464 <nick> :Password incorrect` |
| **NUM-25** | `471 ERR_CHANNELISFULL` | `:<server> 471 <nick> <channel> :Cannot join channel (+l)` |
| **NUM-26** | `473 ERR_INVITEONLYCHAN` | `:<server> 473 <nick> <channel> :Cannot join channel (+i)` |
| **NUM-27** | `475 ERR_BADCHANNELKEY` | `:<server> 475 <nick> <channel> :Cannot join channel (+k)` |
| **NUM-28** | `482 ERR_CHANOPRIVSNEEDED` | `:<server> 482 <nick> <channel> :You're not channel operator` |
