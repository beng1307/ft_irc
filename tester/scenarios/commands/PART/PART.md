# Comprehensive PART Command Flow & Edge Case Analysis

This document provides an exhaustive, line-by-line breakdown of the `PART` command lifecycle in `ft_irc`. It details input grammar edge cases, state transitions, security vulnerabilities, command interactions, channel cleanup mechanics, memory & socket state consistency, and reachable failure modes.

---

## 1. Flow Overview & Architecture

### High-Level Architecture Flowchart
```
                      [Raw Socket Stream]
                               │
                               ▼
                      Server::handle_client_input (reads up to 512 bytes)
                               │
                               ▼
                      Server::handle_line (extracts line delimited by \r\n)
                               │
                               ▼
                      Server::split_arguments (splits by ' ', ignores empty tokens)
                               │
                               ▼
                      Server::dispatch_command
                               │
         ┌─────────────────────┴─────────────────────┐
         ▼                                           ▼
[Unregistered Client]                       [Registered Client]
!client.get_register_status()                command == "PART"
         │                                           │
         ▼                                           ▼
send_status(451,                            Server::handle_part_command
":You have not registered")                         │
                                                    ▼
                                    arguments.empty()? ──Yes──► send_status(461, "PART :Not enough parameters")
                                                    │ No
                                                    ▼
                                    Extract reason:
                                    if line.contains(" :") -> line.strAfter(" :")
                                    else -> empty ""
                                                    │
                                                    ▼
                                    Server::part_client_from_channel(client, arguments[0], reason)
                                                    │
                                                    ▼
                                    Channel &channel = get_channel(channel_name)
                                    !channel (Channel not found in Server)?
                                                    │
                                          ┌─────────┴─────────┐
                                          ▼                   ▼
                                        [Yes]                [No]
                                  send_status(403,     channel.has_member(client.get_socket())?
                             "<chan> :No such channel")       │
                                                    ┌─────────┴─────────┐
                                                    ▼                   ▼
                                                  [No]                [Yes]
                                            send_status(442,    channel.broadcast(client, "PART", reason)
                                    "<chan> :You're not               │
                                           on that channel")          ▼
                                                                channel.remove_client_from_channel(client_fd)
                                                                      │
                                                                      ├─► remove_invited(client_fd)
                                                                      ├─► remove_operator(client_fd)
                                                                      ├─► remove_member(client_fd)
                                                                      ▼
                                                                channel.empty()?
                                                                      │
                                                                ┌─────┴─────┐
                                                                ▼           ▼
                                                              [Yes]        [No]
                                                        remove_channel   Channel remains active
                                                        (erased from     (may become opless if
                                                         server map)      sole op departed)
```

---

## 2. Line-by-Line Code Analysis & Edge Case Inventory

### A. Input Parsing & Grammar Edge Cases (`ServerCommands.cpp`, `ServerHelper.cpp`)

#### 1. Multi-Channel PART Rejection / Misinterpretation (`PART #chan1,#chan2`)
- **Code Reference**: `ServerCommands.cpp:203-215`
  ```cpp
  void Server::handle_part_command(Client &client, const Wire &line, const Vector<Wire> &arguments)
  {
      if (arguments.empty())
      {
          send_status(client, "461", "PART :Not enough parameters");
          return ;
      }
      Wire reason;
      if (line.contains(" :"))
          reason = line.strAfter(" :");
      part_client_from_channel(client, arguments[0], reason);
  }
  ```
- **RFC Standard (RFC 2812 §3.2.2)**:
  `PART <channel>{,<channel>} [<Part Message>]`
  Clients are allowed to leave multiple channels in one command, e.g.:
  `PART #chan1,#chan2 :Leaving all`
- **Flaw**: `arguments[0]` is taken as a single literal channel name string.
- **Observed Behavior**: If client sends `PART #chan1,#chan2`, the server queries `get_channel("#chan1,#chan2")`. Since no channel with the literal name `"#chan1,#chan2"` exists, server responds with `403 #chan1,#chan2 :No such channel`. Neither `#chan1` nor `#chan2` is parted.
- **Failure Impact**: Auto-part scripts, bouncers (ZNC), and standard IRC clients sending comma-delimited channel lists fail to part their rooms.

#### 2. Reason Argument Parsing Flaw: Trailing vs Single-Token Reason (`PART #chan reason_without_colon`)
- **Code Reference**: `ServerCommands.cpp:211-214`
  ```cpp
  Wire reason;
  if (line.contains(" :"))
      reason = line.strAfter(" :");
  part_client_from_channel(client, arguments[0], reason);
  ```
- **Flaw**: The reason is ONLY extracted if `line` contains `" :"`. If a user or client sends `PART #chan Goodbye` (without a leading colon for a single-word parameter), `line.contains(" :")` evaluates to `false`.
- **Observed Behavior**: The reason becomes empty `""`. `arguments[1]` is completely discarded. The broadcast sent to channel members will omit the part message (`:nick!user@host PART #chan`).
- **RFC Standard**: An argument without a leading colon is a valid trailing parameter if it is the last token or has no spaces.

#### 3. False Positive Reason Splitter with `" :"` Inside Parameters or Nickname
- **Code Reference**: `ServerCommands.cpp:212-213`
  ```cpp
  if (line.contains(" :"))
      reason = line.strAfter(" :");
  ```
- **Flaw**: `line.contains(" :")` searches from index 0 of the raw line.
- **Edge Cases**:
  - `PART :#chan :Goodbye`: If a client library prepends a colon to the first parameter, `line.strAfter(" :")` matches after `#chan` or after the first colon, corrupting either channel name or reason.
  - `PART #chan`: `line.contains(" :")` is false $\to$ `reason = ""`.
  - `PART #chan :`: `line.contains(" :")` is true $\to$ `reason = ""`.
  - `PART #chan   :hello`: Multiple spaces before colon $\to$ `strAfter(" :")` correctly extracts `"hello"`.
  - `PART #chan:key`: If no space before colon $\to$ `contains(" :")` is false.

#### 4. Colon-Prefixed Channel Parameter (`PART :#chan`)
- **Code Reference**: `ServerHelper.cpp:39-42` (`split_arguments`)
  ```cpp
  Vector<Wire> Server::split_arguments(const Wire &line)
  {
      return line.strAfter(" ").splitBy(' ').filter(is_empty);
  }
  ```
- **Flaw**: `split_arguments` does not strip the RFC prefix colon (`:`) from arguments.
- **Behavior**: For `PART :#chan`, `arguments[0]` is `":#chan"`. Then `get_channel(":#chan")` looks up `":#chan"` in the channel map and returns a non-existent channel, yielding `403 :#chan :No such channel`.

#### 5. Unregistered Client Rejection (`451 ERR_NOTREGISTERED`)
- **Code Reference**: `ServerCommands.cpp:303-304`
  ```cpp
  else if (!client.get_register_status())
      send_status(client, "451", ":You have not registered");
  ```
- **Behavior**: An unregistered connection sending `PART #chan` receives `451 :You have not registered`. No channel state or map is accessed.

#### 6. Missing Parameter Rejection (`461 ERR_NEEDMOREPARAMS`)
- **Code Reference**: `ServerCommands.cpp:206-210`
  ```cpp
  if (arguments.empty())
  {
      send_status(client, "461", "PART :Not enough parameters");
      return ;
  }
  ```
- **Behavior**: `PART` or `PART   ` returns `:localhost 461 <nick> PART :Not enough parameters`.

---

### B. Channel State & Membership Edge Cases (`ServerCommands.cpp`, `Channel.cpp`)

#### 1. Non-Existent Channel (`403 ERR_NOSUCHCHANNEL`)
- **Code Reference**: `ServerCommands.cpp:76-81`
  ```cpp
  Channel &channel = get_channel(channel_name);
  if (!channel)
  {
      send_status(client, "403", channel_name + " :No such channel");
      return ;
  }
  ```
- **Behavior**: If `#nonexistent` is queried, `get_channel` returns a default invalid Channel object (`_ok == false`). Server emits `403 #nonexistent :No such channel`.

#### 2. Channel Exists But Client Is Not A Member (`442 ERR_NOTONCHANNEL`)
- **Code Reference**: `ServerCommands.cpp:83-87`
  ```cpp
  if (!channel.has_member(client.get_socket()))
  {
      send_status(client, "442", channel_name + " :You're not on that channel");
      return ;
  }
  ```
- **Behavior**: Client is not in `channel.member_fds`. Server emits `442 #channel :You're not on that channel`.

#### 3. Case Sensitivity in Channel Lookup (`PART #Test` vs `PART #test`)
- **Code Reference**: `Server.cpp:165-168`, `ChannelMap`
  ```cpp
  Channel &Server::get_channel(const Wire &name)
  {
      return (channels.fetch(name));
  }
  ```
- **Flaw**: `ChannelMap` (underlying `std::map<Wire, Channel>`) performs case-sensitive string matching (`Wire::operator<`).
- **Behavior**: If channel `#test` was created with `JOIN #test`, a client typing `PART #Test` will fail with `403 #Test :No such channel` (or `442` if `#Test` was independently created).
- **RFC Standard**: Channel names are case-insensitive ASCII (`#test` == `#TEST`).

#### 4. The "Last Member Leaving" Channel Destruction Lifecycle
- **Code Reference**: `Channel.cpp:118-125`
  ```cpp
  void Channel::remove_client_from_channel(int client_fd)
  {
      remove_invited(client_fd);
      remove_operator(client_fd);
      remove_member(client_fd);
      if (empty() && server)
          server->remove_channel(name);
  }
  ```
- **Flow**:
  1. Client sends `PART #chan`.
  2. Broadcast `:nick!user@host PART #chan` is dispatched to all members (including the parting client).
  3. `remove_client_from_channel` clears `client_fd` from `invited_fds`, `operator_fds`, `member_fds`.
  4. `empty()` evaluates to `true` (size == 0).
  5. `server->remove_channel(name)` executes `channels.erase(name)`.
  6. The channel object and all its stored metadata (`topic`, `channel_key`, `user_limit`, `invite_only`, `topic_restricted`) are destroyed and deallocated.
- **Consequence**: When the next user joins `#chan`, it is a brand-new channel with default modes (`-i`, `-t`, `-k`, `-l`, no topic, fresh operator).

#### 5. Sole Channel Operator Departure $\to$ "Opless Channel" Stagnation
- **Scenario**: Channel has 3 members: Client A (operator), Client B (regular), Client C (regular).
- **Flow**: Client A sends `PART #chan`.
- **State Result**:
  - `member_fds` contains `{B, C}`.
  - `operator_fds` becomes `{}` (EMPTY).
  - The channel remains active because `empty()` is `false`.
- **System Impact**:
  - Neither B nor C can execute `KICK`, `INVITE` (if `+i`), or `MODE` changes.
  - If `+t` (topic restriction) was active, NOBODY can ever change the topic again.
  - If `+i` (invite-only) was active and a non-member wants to join, NOBODY can invite them.
  - The channel remains in an immutable "zombie op" state until all remaining members part and recreate it.

#### 6. Double PART / Rapid Re-PART Divergent Error Codes
- **Scenario**: Client sends two consecutive `PART #chan` commands back-to-back:
  - **Variant A (Multi-user channel)**:
    - 1st PART: Client removed, broadcast sent.
    - 2nd PART: Channel still exists $\to$ `channel.has_member(fd)` is `false` $\to$ Returns `442 #chan :You're not on that channel`.
  - **Variant B (Single-user channel)**:
    - 1st PART: Client removed $\to$ Channel erased from server.
    - 2nd PART: Channel no longer exists $\to$ Returns `403 #chan :No such channel`.
- **Observation**: The server produces different error codes (`442` vs `403`) for the exact same invalid second command depending purely on whether other users were in the channel.

---

### C. Message Formatting & Broadcast Delivery Mechanics (`ServerMessaging.cpp`, `Channel.cpp`)

#### 1. Broadcast Audience Includes the Parting Client
- **Code Reference**: `ServerCommands.cpp:89`, `Channel.cpp:265-267`
  ```cpp
  channel.broadcast(client, "PART", reason);
  channel.remove_client_from_channel(client.get_socket());
  ```
  ```cpp
  void Channel::broadcast(const Client &client, const Wire &cmd, const Wire &param) const
  {
      broadcast(make_msg(client, cmd, name, param));
  }
  ```
- **Flow**: `channel.broadcast(...)` sends to all `member_fds` *before* `remove_client_from_channel` is invoked.
- **Format Verification**:
  - With reason: `make_msg` outputs `:<nick>!<user>@localhost PART <channel> :<reason>\r\n`.
  - Without reason: `make_msg` outputs `:<nick>!<user>@localhost PART <channel>\r\n`.
- **RFC Standard Compliance**: Parting client is mandated to receive their own PART confirmation so the client UI updates local state.

#### 2. Reason Sanitization & Empty Colon Handling
- **Inputs & Message Outputs**:
  - Input: `PART #chan :Leaving now` $\to$ `:nick!user@localhost PART #chan :Leaving now`
  - Input: `PART #chan :` $\to$ `:nick!user@localhost PART #chan` (trailing empty colon avoided)
  - Input: `PART #chan :   spaced text   ` $\to$ `:nick!user@localhost PART #chan :   spaced text   `
  - Input: `PART #chan :reason with : colon : inside` $\to$ `:nick!user@localhost PART #chan :reason with : colon : inside`

---

### D. Inter-Command Interactions & Ripple Effects

| Interacting Command | Interaction Flow & Sequence | Reachable Edge Case / State Anomaly |
| :--- | :--- | :--- |
| **PART + QUIT** | Client sends `PART #chan\r\nQUIT :bye\r\n` in a single TCP packet. | Server processes `PART #chan` first $\to$ client removed from channel $\to$ channel destroyed if empty. Server then processes `QUIT` $\to$ `get_client_audience` finds 0 mutual channels $\to$ no QUIT broadcast sent to ex-channel mates. |
| **PART + NICK** | Client parts channel, then immediately changes nickname (`NICK newnick`). | Because client is no longer in `#chan`, previous channel members do not receive the `NICK` change notification. |
| **PART + KICK** | Operator kicks target client at the exact same moment target sends `PART`. | If `PART` arrives first: Target is removed. When `KICK` executes: `ensure_channel_member` fails with `441 target #chan :They aren't on that channel`. If `KICK` arrives first: Target receives KICK. Target's `PART` fails with `442`. |
| **PART + PRIVMSG (Outgoing)** | Client sends `PART #chan` followed by `PRIVMSG #chan :one last word`. | When `PRIVMSG` executes, `send_message_to_channel` checks `!channel.has_member(fd)` $\to$ yields `442 #chan :You're not on that channel`. Message blocked. |
| **PART + PRIVMSG (Incoming)** | Another user sends `PRIVMSG #chan :hi` right after client's `PART`. | Parted client does NOT receive the message because `member_fds` no longer includes their FD. |
| **PART + TOPIC** | Client parts channel and sends `TOPIC #chan`. | `handle_topic` enforces `ensure_channel_member` $\to$ yields `442 #chan :You're not on that channel`. Non-members cannot read channel topic. |
| **PART + INVITE** | Op invites User B (`INVITE B #chan`), then Op parts (`PART #chan`). | If channel was NOT empty: User B remains in `invited_fds` and can still join `+i` channel later without active Op. If Op was sole member: Channel is erased; all pending invites are destroyed. |
| **PART + MODE (+k/+l/+t/+i)** | Op sets modes (`+k pass`, `+l 5`, etc.) then parts. | If other members remain: Channel modes stay locked in place with no operator to manage them. If last member parts: All mode flags wiped cleanly on channel destruction. |
| **PART + JOIN (Re-join)** | Client parts `#chan` and immediately sends `JOIN #chan`. | If client was the only member: Rejoining creates a fresh channel; client re-acquires operator status (`@`). If other members remained: Client rejoins as regular non-op member (subject to `+i`, `+k`, `+l` restrictions). |

---

### E. Socket, FD, and Memory Lifecycle

#### 1. Zero Channel Retention After All-Channel PART
- When a client executes `PART` on all channels they previously joined:
  - Client remains connected on TCP socket.
  - Client state in `Server::clients` is unchanged (`is_registered == true`).
  - Client can execute private messages (`PRIVMSG <nick>`), query capabilities, or join other channels without reconnecting.

#### 2. FD Cleanliness on PART vs DISCONNECT
- In `Channel::remove_client_from_channel(fd)` (called during `PART` and `KICK`):
  - `invited_fds.erase(fd)` $\checkmark$
  - `operator_fds.erase(fd)` $\checkmark$
  - `member_fds.erase(fd)` $\checkmark$
- Unlike `disconnect_client` (which only erased from `member_fds`), `PART` guarantees complete cleanup of all channel-internal sets for the departing socket descriptor.

#### 3. Send Buffer / SendQ Integrity during PART Broadcast
- During `channel.broadcast(client, "PART", reason)`:
  - Each recipient's `out_buffer` receives the message.
  - If a recipient socket buffer is congested, `POLLOUT` is armed.
  - If a recipient's `out_buffer` exceeds `MAX_OUTPUT_BUFFER_SIZE` (1 MB), `disconnect_client` safely terminates the lagging recipient.
  - `Channel::broadcast` iterates over a temporary snapshot `member_fds.subtract(except_fd)`, preventing iterator corruption during broadcast.

---

## 3. Comprehensive Edge Case & Attack Surface Matrix

| ID | Edge Case Category | Input / Trigger Scenario | Server Branch Reached | Expected / Actual Result | RFC Standard & Severity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EC-01** | Multi-channel batch | `PART #chan1,#chan2` | `get_channel("#chan1,#chan2")` | Fails with `403 #chan1,#chan2 :No such channel`. | RFC 2812 §3.2.2 violation. Med severity. |
| **EC-02** | Colon-prefixed target | `PART :#test` | `get_channel(":#test")` | Fails with `403 :#test :No such channel`. | RFC 2812 §2.3.1 violation. Low severity. |
| **EC-03** | Missing parameters | `PART` or `PART   ` | `arguments.empty()` | `461 PART :Not enough parameters`. | RFC compliant. Normal. |
| **EC-04** | Unregistered client | `PART #test` before PASS/NICK/USER | `!client.get_register_status()` | `451 :You have not registered`. | RFC compliant. Normal. |
| **EC-05** | Non-existent channel | `PART #nonexistent` | `!channel` in `part_client_from_channel` | `403 #nonexistent :No such channel`. | RFC compliant. Normal. |
| **EC-06** | Not on channel | `PART #chan` (client not joined) | `!channel.has_member(fd)` | `442 #chan :You're not on that channel`. | RFC compliant. Normal. |
| **EC-07** | Reason without colon | `PART #chan Goodbye` | `!line.contains(" :")` | Reason ignored; broadcasts without message. | Grammar discrepancy. Low severity. |
| **EC-08** | Reason with colon | `PART #chan :Goodbye all` | `line.contains(" :")` | Broadcasts `PART #chan :Goodbye all`. | RFC compliant. Normal. |
| **EC-09** | Empty colon reason | `PART #chan :` | `strAfter(" :") == ""` | Broadcasts `PART #chan`. | RFC compliant. Normal. |
| **EC-10** | Sole member parts | Client alone in `#chan` parts | `channel.empty() == true` | Channel erased from server map. | Expected cleanup. Normal. |
| **EC-11** | Sole operator parts | Operator parts while others remain | `remove_operator(fd)` | Channel becomes permanently opless. | IRC architectural quirk. Med impact. |
| **EC-12** | Non-op member parts | Regular user parts | `remove_member(fd)` | Op remains op, member removed. | Normal flow. |
| **EC-13** | Rapid double PART (solo) | Solo user sends `PART #chan` x2 | 1st: Erased; 2nd: `!channel` | 1st: PART; 2nd: `403 :No such channel`. | Micro-variation. |
| **EC-14** | Rapid double PART (multi) | User sends `PART #chan` x2 (others in chan) | 1st: Removed; 2nd: `!has_member` | 1st: PART; 2nd: `442 :You're not on that channel`. | Micro-variation. |
| **EC-15** | Pipelined PART + PRIVMSG | `PART #c\r\nPRIVMSG #c :msg\r\n` | 1st: Parted; 2nd: `!has_member` | 1st: PART; 2nd: `442 :You're not on that channel`. | Normal. |
| **EC-16** | Pipelined PART + QUIT | `PART #c\r\nQUIT :bye\r\n` | 1st: Parted; 2nd: `get_audience` | Audience empty; ex-members get no QUIT msg. | RFC compliant. |
| **EC-17** | Case mismatch | `JOIN #test` then `PART #TEST` | `ChannelMap` case-sensitive fetch | Fails with `403 #TEST :No such channel`. | RFC 2812 violation. Med severity. |
| **EC-18** | Reason with colons | `PART #chan :msg:with:colons` | `strAfter(" :")` | Correctly preserves `"msg:with:colons"`. | RFC compliant. Normal. |
| **EC-19** | Trailing whitespace reason | `PART #chan :bye   ` | `strAfter(" :")` | Preserves trailing spaces. | RFC compliant. Normal. |
| **EC-20** | Non-channel string | `PART user` or `PART invalid` | `get_channel("user")` | Returns `403 user :No such channel`. | RFC compliant. Normal. |

---
