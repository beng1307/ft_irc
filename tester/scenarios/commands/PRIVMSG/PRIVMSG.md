# Detailed PRIVMSG Command Analysis: Lifecycle, Edge Cases & Interactions

A comprehensive, line-by-line audit of the `PRIVMSG` command implementation in `ft_irc` across the entire codebase (`ServerCommands.cpp`, `ServerMessaging.cpp`, `ServerLoop.cpp`, `ServerHelper.cpp`, `ServerSocket.cpp`, `Channel.cpp`, `Channel.hpp`, `Client.cpp`, `Client.hpp`, `Wire.hpp`).

---

## Table of Contents
1. [End-to-End Flow Diagram](#1-end-to-end-flow-diagram)
2. [Code Trace & State Transitions](#2-code-trace--state-transitions)
3. [Deep Edge Case Matrix](#3-deep-edge-case-matrix)
   - [A. Input Parsing & Grammar Edge Cases](#a-input-parsing--grammar-edge-cases)
   - [B. Channel Messaging Edge Cases](#b-channel-messaging-edge-cases)
   - [C. Direct User Messaging Edge Cases](#c-direct-user-messaging-edge-cases)
   - [D. Socket, Buffer & Transport Edge Cases](#d-socket-buffer--transport-edge-cases)
4. [Command Interactions & Cross-Command Cascades](#4-command-interactions--cross-command-cascades)
   - [1. PRIVMSG + JOIN / PART / KICK](#1-privmsg--join--part--kick)
   - [2. PRIVMSG + NICK Change](#2-privmsg--nick-change)
   - [3. PRIVMSG + QUIT / Disconnect / SendQ Exceeded](#3-privmsg--quit--disconnect--sendq-exceeded)
   - [4. PRIVMSG + MODE (+i, +k, +l, +t, +o)](#4-privmsg--mode-i-k-l-t-o)
   - [5. PRIVMSG + Self-Targeting & Echo](#5-privmsg--self-targeting--echo)
   - [6. PRIVMSG + Unregistered / Partial Registration](#6-privmsg--unregistered--partial-registration)
5. [Summary of Critical Vulnerabilities & Actionable Recommendations](#5-summary-of-critical-vulnerabilities--actionable-recommendations)

---

## 1. End-to-End Flow Diagram

```
[ TCP Socket Inbound: "PRIVMSG <target> :<message>\r\n" or "PRIVMSG <target> <text>\r\n" ]
                             │
                             ▼
[ ServerLoop.cpp: handle_client_input ]
   ├─► recv() into buffer
   ├─► client.append_raw_buffer(buffer, bytes_received)
   ├─► input_exceeds_irc_line_limit() check (> 510 bytes without \r\n)
   │        └─► EXCEEDS: disconnect_client(client_fd) -> RETURN
   └─► find("\r\n") loop
            │
            ▼
[ ServerCommands.cpp: handle_line(client, position) ]
   ├─► line = client.get_buffer().substr(0, position)
   ├─► client.get_buffer().erase(0, position + 2)
   ├─► command = line.splitBy(' ')[0].toUpper()
   ├─► arguments = split_arguments(line) -> line.strAfter(" ").splitBy(' ').filter(is_empty)
   └─► dispatch_command(client, "PRIVMSG", line, arguments)
            │
            ▼
[ ServerCommands.cpp: dispatch_command ]
   ├─► Registration Check: !client.get_register_status()
   │        └─► UNREGISTERED: send_status(client, "451", ":You have not registered") -> RETURN
   └─► Route to handle_privmsg_command(client, line, arguments)
            │
            ▼
[ ServerCommands.cpp: handle_privmsg_command ]
   │
   ├─► 1. Parameter Count Check: arguments.empty()
   │        └─► YES: send_status(client, "411", ":No recipient given (PRIVMSG)") -> RETURN
   │
   ├─► 2. Extract Message Text:
   │        ├─► IF line.contains(" :"): message = line.strAfter(" :")
   │        ├─► ELSE IF arguments.size() > 1: message = arguments[1]  <-- (Drops trailing words if >2 args without colon!)
   │        └─► ELSE: message is empty
   │
   ├─► 3. Empty Message Check: message.empty()
   │        └─► YES: send_status(client, "412", ":No text to send") -> RETURN
   │
   ├─► 4. Target Routing Decision:
   │        ├─► IF !target.empty() && target[0] == '#':
   │        │        └─► send_message_to_channel(client, target, message)
   │        │
   │        └─► ELSE: (Note: channels starting with '&' fall into user routing!)
   │                 └─► send_message_to_user(client, target, message)
   │
   ├─► 5A. Channel Routing (send_message_to_channel):
   │        ├─► Channel exists? Channel &channel = get_channel(channel_name)
   │        │        └─► NOT FOUND: send_status(sender, "403", channel_name + " :No such channel") -> RETURN
   │        ├─► Sender is member? channel.has_member(sender.get_socket())
   │        │        └─► NOT MEMBER: send_status(sender, "442", channel_name + " :You're not on that channel") -> RETURN
   │        └─► Broadcast: channel.broadcast_from(sender, "PRIVMSG", message)
   │                 ├─► Excludes sender's fd: member_fds.subtract(sender_fd)
   │                 └─► Sends to each member: ":sender_nick!sender_user@localhost PRIVMSG #channel :message\r\n"
   │
   └─► 5B. User Routing (send_message_to_user):
            ├─► Target client exists? Client &target = get_client(nickname)
            │        └─► NOT FOUND: send_status(sender, "401", nickname + " :No such nick/channel") -> RETURN
            └─► Unicast Send:
                     target.send(make_msg(sender, "PRIVMSG", nickname, message))
                     └─► Sends: ":sender_nick!sender_user@localhost PRIVMSG recipient_nick :message\r\n"
```

---

## 2. Code Trace & State Transitions

### State Variables Involved:
- `Client::is_registered` (`bool`): Checked in `dispatch_command`. Must be `true` for sender. (Target client registration is NOT checked in `send_message_to_user`).
- `Client::nickname` (`Wire`): Prefix sender nickname and destination target match.
- `Client::username` (`Wire`): Prefix sender username.
- `Channel::member_fds` (`Set<int>`): Set of active channel member sockets used to compute recipient list.
- `Client::out_buffer` (`Wire`): Outbound queue on non-blocking sockets.
- `Server::clients` (`ClientMap`): Map of socket fd to `Client` objects.
- `Server::channels` (`ChannelMap`): Map of channel names to `Channel` objects.

---

## 3. Deep Edge Case Matrix

### A. Input Parsing & Grammar Edge Cases

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A1** | `PRIVMSG &localchan :Hello` (local channel starting with `&`) | Deliver to members of channel `&localchan` | **Routed to `send_message_to_user`!** Checks for user named `&localchan` -> returns `401 ERR_NOSUCHNICK` | **HIGH** | `handle_privmsg_command` strictly checks `channel_or_user_name[0] == '#'`. However, `handle_join_command` permits channels starting with `&`. |
| **A2** | `PRIVMSG target word1 word2 word3` (multi-word message without colon) | Deliver `"word1 word2 word3"` to target | **Truncates to `"word1"` only!** (`arguments[1]`), dropping `"word2 word3"` entirely | **MEDIUM** | `handle_privmsg_command` checks `else if (arguments.size() > 1) message = arguments[1];` instead of joining all trailing arguments. |
| **A3** | `PRIVMSG target :` (trailing colon with empty payload) | `412 ERR_NOTEXTTOSEND` | Sends `412 :No text to send` | OK | `line.strAfter(" :")` returns empty string, triggering `message.empty()` check. |
| **A4** | `PRIVMSG target :   ` (payload of only whitespace) | Deliver spaces or send `412` | Delivers `"   "` to recipient | OK | Non-empty string delivered as valid text payload. |
| **A5** | `PRIVMSG target  :Double space before colon` | Deliver `"Double space before colon"` | `strAfter(" :")` leaves one extra leading space in message payload | **LOW** | `strAfter(" :")` assumes exactly one space precedes the colon. |
| **A6** | `PRIVMSG target :Hello :World :123` (internal colons) | Deliver `"Hello :World :123"` | Delivers `"Hello :World :123"` | OK | `strAfter(" :")` splits only on the first `" :"`, preserving internal colons. |
| **A7** | `PRIVMSG` (no recipient, no message) | `411 ERR_NORECIPIENT` | Sends `411 :No recipient given (PRIVMSG)` | OK | `arguments.empty()` caught immediately. |
| **A8** | `PRIVMSG target` (recipient given, no text) | `412 ERR_NOTEXTTOSEND` | Sends `412 :No text to send` | OK | `line.contains(" :")` is false, `arguments.size() == 1`, `message` is empty. |
| **A9** | `PRIVMSG target1,target2 :Hello` (comma-separated recipient list) | Deliver to both `target1` and `target2` | Searches for single target literally named `"target1,target2"` -> `401` or `403` | **MEDIUM** | RFC 2812 §3.3.1 multi-target messaging is not parsed/supported. |
| **A10**| `PRIVMSG :target :Hello` (leading colon before recipient parameter) | Deliver to `target` | `arguments[0]` becomes `":target"`, lookup fails with `401` or `403` | **LOW** | Leading colon on parameters before trailing parameter is not stripped. |
| **A11**| `PRIVMSG target :\x01ACTION waves\x01` (CTCP ACTION / query) | Pass CTCP payload transparently | Passed as normal PRIVMSG payload | OK | CTCP encapsulation requires no special server manipulation. |
| **A12**| Case sensitivity in target: `PRIVMSG #CHANNEL :hi` vs `JOIN #channel` | Match channel case-insensitively | Exact match lookup fails -> `403 :No such channel` | **HIGH** | `ChannelMap` and `get_channel()` do exact string comparison without case folding. |
| **A13**| Case sensitivity in nick target: `PRIVMSG ALICE :hi` vs `NICK Alice` | Match nickname case-insensitively | `get_client` equality check fails -> `401 ALICE :No such nick/channel` | **HIGH** | `match_nickname` uses `c.get_nickname() == nick` (case-sensitive) instead of `toLower()`. |

---

### B. Channel Messaging Edge Cases

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B1** | Non-member sends message to `#chan` | `404 ERR_CANNOTSENDTOCHAN` | Sends `442 <channel> :You're not on that channel` | **MEDIUM** | Code returns numeric `442` instead of standard `404`. |
| **B2** | Message to non-existent channel `PRIVMSG #ghost :hi` | `403 ERR_NOSUCHCHANNEL` | Sends `403 #ghost :No such channel` | OK | `ensure_channel_exists` / `get_channel` validation correctly handled. |
| **B3** | Sender receiving own channel message (Echo) | Sender should NOT receive own broadcast | Sender socket is excluded via `except_fd` in `broadcast_from` | OK | `channel.broadcast_from(sender, "PRIVMSG", message)` subtracts sender fd. |
| **B4** | Channel with only 1 member (the sender) | No error, message absorbed silently | Sender excluded, loop over empty set, returns silently | OK | Standard IRC broadcast behavior. |
| **B5** | Channel mode `+t` (topic restricted) active | Normal PRIVMSG allowed | PRIVMSG allowed (only TOPIC restricted) | OK | Channel topic mode does not restrict PRIVMSG. |
| **B6** | Channel mode `+k`, `+i`, `+l` active | Existing members can send PRIVMSG freely | Members can send PRIVMSG freely | OK | Membership modes only restrict `JOIN`, not member messaging. |

---

### C. Direct User Messaging Edge Cases

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | `PRIVMSG Alice :hi` when Alice does not exist | `401 ERR_NOSUCHNICK` | Sends `401 Alice :No such nick/channel` | OK | Handled in `send_message_to_user`. |
| **C2** | `PRIVMSG Alice :hi` when Alice is connected but UNREGISTERED | `401 ERR_NOSUCHNICK` (unregistered user invisible) | **Delivers PRIVMSG to unregistered client!** | **HIGH** | `send_message_to_user` checks `if (!target)` but does NOT check `target.get_register_status()`. Unregistered clients receive private messages before completing handshake. |
| **C3** | Self-messaging: `PRIVMSG sender_nick :self note` | Deliver message back to sender | Message delivered to sender via unicast | OK | Direct messaging to self is valid in IRC. |
| **C4** | Hostname formatting in message prefix | `:nick!user@<host>` | Hardcoded to `:nick!user@localhost` | OK | Consistent with project host configuration. |

---

### D. Socket, Buffer & Transport Edge Cases

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **D1** | Slow recipient socket buffer full (EAGAIN/EWOULDBLOCK) | Queue message in `out_buffer` and arm `POLLOUT` | Appends to `out_buffer`, enables `POLLOUT` in pollfd, drains on next writable event | OK | Robust non-blocking event-driven SendQ mechanism in `ServerLoop.cpp`. |
| **D2** | Massive channel broadcast flooding recipient (> 1MB SendQ) | Disconnect overflowing client ("SendQ exceeded") | `disconnect_client(fd)` called when `out.size() > MAX_OUTPUT_BUFFER_SIZE` | OK | Prevents unbounded server memory leak from unresponsive clients. |
| **D3** | Member disconnected mid-broadcast due to socket error | Other channel members still receive message | Iteration uses snapshot `Set<int>` of member FDs; `send_string_fn` checks `if (client)` before sending | OK | Clean iteration safety; no null pointer dereference or crash. |
| **D4** | Inbound line exceeds 510 bytes | Disconnect client per IRC line limit | `input_exceeds_irc_line_limit` detects overflow and disconnects client | OK | Defends against buffer overflow / memory flooding attacks. |
| **D5** | Outbound generated line exceeds 512 bytes | Truncate or deliver | Server sends full outbound payload to socket without truncation | **LOW** | Receiving client with strict 512-byte buffer may truncate trailing bytes. |
| **D6** | Embedded `\r` or `\n` in message payload | Strip or reject to prevent protocol injection | Since splitting strictly uses `\r\n`, a lone `\r` or `\n` inside payload passes into outbound stream, causing CRLF protocol injection | **HIGH** | Outbound string contains raw unescaped newlines if not sanitized. |

---

## 4. Command Interactions & Cross-Command Cascades

### 1. PRIVMSG + JOIN / PART / KICK
- **Race Condition / State Flow**:
  1. Client A joins `#chan` (`JOIN #chan`).
  2. Client B immediately sends `PRIVMSG #chan :Welcome!`.
  3. Since `add_member` is synchronous, Client A is already in `member_fds` and immediately receives the message.
  4. If Client A is kicked (`KICK #chan Alice`) or parts (`PART #chan`), `remove_member` is synchronous.
  5. Subsequent `PRIVMSG #chan` by Alice immediately returns `442 :You're not on that channel`.
  6. Subsequent `PRIVMSG #chan` by other members no longer delivers to Alice.

### 2. PRIVMSG + NICK Change
- **Scenario**:
  1. User `Alice` executes `NICK Alicia`.
  2. User `Bob` sends `PRIVMSG Alice :Hello`.
- **Behavior**:
  - `get_client("Alice")` searches active client nicknames. Since Alice's nickname is now `Alicia`, the lookup fails.
  - Server sends `401 Alice :No such nick/channel`.
  - Bob must address subsequent messages to `Alicia`.

### 3. PRIVMSG + QUIT / Disconnect / SendQ Exceeded
- **Scenario**:
  1. User `Bob` executes `QUIT :Leaving`.
  2. Server sets `Bob.should_disconnect(true)` and queues `ERROR :Closing connection` in `Bob.out_buffer`.
  3. Before socket drains and closes, User `Alice` sends `PRIVMSG Bob :Wait don't go!`.
- **Behavior**:
  - Because Bob is still in `clients` map pending buffer drain, `get_client("Bob")` succeeds.
  - The PRIVMSG is appended to Bob's `out_buffer`.
  - Once the buffer drains on `POLLOUT`, `send_to_client` detects `out.empty()` and `should_disconnect() == true`, and finalizes `disconnect_client(Bob_fd)`.
  - Once disconnected, subsequent `PRIVMSG Bob` from Alice returns `401 :No such nick/channel`.

### 4. PRIVMSG + MODE (+i, +k, +l, +t, +o)
- **Scenario**:
  - Channel operator sets `+i` (invite-only), `+k` (key), `+l` (limit), or `+t` (topic restricted).
- **Behavior**:
  - Existing members who joined previously can continue to exchange `PRIVMSG` without restriction.
  - Channel modes `+i`, `+k`, `+l` only gate the `JOIN` command.
  - Channel mode `+t` only gates the `TOPIC` command.
  - None of these modes block regular member communication on the channel.

### 5. PRIVMSG + Self-Targeting & Echo
- **Scenario A: Direct Message to Self (`PRIVMSG Alice :note`)**:
  - `get_client("Alice")` resolves to Alice's own Client instance.
  - `target.send(...)` transmits `:Alice!user@localhost PRIVMSG Alice :note` back to Alice.
- **Scenario B: Channel Message (`PRIVMSG #chan :hello`)**:
  - `channel.broadcast_from` uses `member_fds.subtract(sender_fd)`.
  - Sender never receives an echo of their own channel broadcast.

### 6. PRIVMSG + Unregistered / Partial Registration
- **Scenario**:
  - Client connects, sends `NICK Bob`, but has NOT sent `PASS` or `USER`.
  - Client Alice (registered) sends `PRIVMSG Bob :Hi Bob`.
- **Behavior**:
  - `send_message_to_user` finds Bob in `clients` map and transmits the PRIVMSG to Bob's socket.
  - Unregistered client Bob receives channel/user messages before receiving `001 RPL_WELCOME`.

### 7. PRIVMSG + Adversarial Attacks & Protocol Breakage
- **LF / CRLF Smuggling**:
  - Malicious sender injects raw `\n` inside payload (`PRIVMSG victim :Hi\nKICK #chan Alice`).
  - Delivered verbatim across TCP stream to victim, creating protocol line desynchronization.
- **Pipelined Post-QUIT PRIVMSG**:
  - Sender pipelines `QUIT\r\nPRIVMSG target :ghost\r\n`.
  - Because disconnection is deferred until buffer drains, subsequent commands in the stream may still execute.
- **Pipelined PART then PRIVMSG**:
  - Client leaves channel with `PART #chan\r\nPRIVMSG #chan :sneaky\r\n` in a single TCP packet.
  - Server must synchronously process `PART` and reject the following `PRIVMSG` with `442` / `404`.
- **Outbound Overlength Line Expansion**:
  - Inbound 500-byte message gets expanded with `:nick!user@localhost PRIVMSG target :` prefix to >560 bytes, violating RFC 512-byte framing limits.
- **Spoofed Client-Supplied Prefixes**:
  - Sender attempts `:admin!admin@localhost PRIVMSG victim :Banned`.
  - Server must reject or ignore client prefixes to prevent identity forgery.
- **Socket FD Reuse Race Isolation**:
  - Client disconnects; newly connected client inherits old FD.
  - PRIVMSG directed to previous client's nickname must fail with `401` and never leak to the new occupant of the FD.

---

## 5. Summary of Critical Vulnerabilities & Actionable Recommendations

| Vulnerability | Impact | Recommended Fix |
| :--- | :--- | :--- |
| **1. `&` Channel Routing Failure** | Local channels starting with `&` cannot receive `PRIVMSG` (treated as nicknames). | Update `handle_privmsg_command`: `if (!target.empty() && (target[0] == '#' \|\| target[0] == '&'))`. |
| **2. Multi-word Parameter Truncation without Colon** | `PRIVMSG target word1 word2` drops everything after `word1`. | Join all arguments starting from index 1 when no ` :` delimiter is present. |
| **3. Case-Sensitive Channel & Nickname Matching** | `PRIVMSG #CHAN` or `PRIVMSG BOB` fails with 403/401 if joined as `#chan` or `Bob`. | Implement case-insensitive comparison (e.g. `toLower()`) for channel and nickname lookups per RFC 2812 §2.2. |
| **4. Direct Messaging Unregistered Clients** | Incomplete connections receive private messages before registration. | In `send_message_to_user`, check `if (!target \|\| !target.get_register_status()) { send_status(sender, "401", ...); return; }`. |
| **5. Numeric Reply 442 instead of 404 for Channel Send** | Non-member sending to channel gets `442 ERR_NOTONCHANNEL` instead of standard `404 ERR_CANNOTSENDTOCHAN`. | Send `404` with `<channel> :Cannot send to channel` in `send_message_to_channel`. |
| **6. Protocol / Line Smuggling via Raw LF** | Unsanitized `\n` in payload allows line injection on downstream client IRC parsers. | Reject or sanitize non-CRLF newline characters in inbound message text. |
| **7. Pipelined Post-QUIT Smuggling** | Commands following `QUIT` in the same input stream are processed before socket close. | Abort line processing loop immediately once `should_disconnect()` is armed. |

