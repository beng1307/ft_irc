# Comprehensive KICK Command Flow & Edge Case Analysis

This document provides an exhaustive, line-by-line breakdown of the `KICK` command lifecycle in `ft_irc` across the entire codebase (`ServerCommands.cpp`, `ServerChannelOps.cpp`, `ServerHelper.cpp`, `ServerMessaging.cpp`, `ServerLoop.cpp`, `Server.cpp`, `Channel.cpp`, `Client.cpp`, and `Wire.hpp`).

It details input grammar edge cases, state transitions, security vulnerabilities, command interactions, channel state consequences, socket/buffer edge cases, and reachable failure modes.

---

## Table of Contents
1. [End-to-End Architecture & Flow Diagram](#1-end-to-end-architecture--flow-diagram)
2. [Code Trace & State Transitions](#2-code-trace--state-transitions)
3. [Deep Edge Case Matrix](#3-deep-edge-case-matrix)
   - [A. Input Parsing & Grammar Edge Cases](#a-input-parsing--grammar-edge-cases)
   - [B. Access Control & Permission Edge Cases](#b-access-control--permission-edge-cases)
   - [C. Identity, Self-Kicking & Op-on-Op Edge Cases](#c-identity-self-kicking--op-on-op-edge-cases)
   - [D. Channel State, Modes & Lifecycle Edge Cases](#d-channel-state-modes--lifecycle-edge-cases)
   - [E. Socket, Buffer & Pipelining Edge Cases](#e-socket-buffer--pipelining-edge-cases)
4. [Command Interactions (What Happens When KICK Interacts With...)](#4-command-interactions)
   - [1. KICK + JOIN / PART / NAMES](#1-kick--join--part--names)
   - [2. KICK + MODE (+o, -o, +i, +k, +l)](#2-kick--mode-o--o-i-k-l)
   - [3. KICK + INVITE](#3-kick--invite)
   - [4. KICK + TOPIC](#4-kick--topic)
   - [5. KICK + PRIVMSG / NOTICE](#5-kick--privmsg--notice)
   - [6. KICK + NICK Collision / Nick Changes](#6-kick--nick-collision--nick-changes)
   - [7. KICK + QUIT / Unexpected Disconnection / SendQ Overflow](#7-kick--quit--unexpected-disconnection--sendq-overflow)
5. [Summary of Identified Vulnerabilities & Failure Modes](#5-summary-of-identified-vulnerabilities--failure-modes)

---

## 1. End-to-End Architecture & Flow Diagram

### High-Level Flow Chart
```
                      [ TCP Inbound Packet: "KICK #chan target :reason\r\n" ]
                                              │
                                              ▼
                               [ ServerLoop.cpp: handle_client_input(fd) ]
                                 - recv() reads into client's raw buffer
                                 - Validates input_exceeds_irc_line_limit (<= 510 bytes)
                                              │
                                              ▼
                               [ ServerCommands.cpp: handle_line(client, pos) ]
                                 - Extracts line = buffer[0..pos]
                                 - Erases [0..pos+2] from client buffer
                                 - Extracts command = line.splitBy(' ')[0].toUpper()
                                 - Validates is_command("KICK") == true
                                 - arguments = split_arguments(line)
                                 - dispatch_command(client, "KICK", line, arguments)
                                              │
                                              ▼
                               [ ServerCommands.cpp: dispatch_command ]
                                 - Checks client.get_register_status()
                                     └─► false ──► send_status(451, ":You have not registered") -> RETURN
                                     └─► true  ──► handle_kick(client, line, arguments)
                                              │
                                              ▼
                        [ ServerChannelOps.cpp: Server::handle_kick ]
                                              │
                                              ▼
                             ┌──────────────────────────────────┐
                             │ 1. Parameter Validation          │
                             │    arguments.size() < 2?         │
                             └────────────────┬─────────────────┘
                                              │ Yes ──► send_status(461, "KICK :Not enough parameters") -> RETURN
                                              │ No
                                              ▼
                             ┌──────────────────────────────────┐
                             │ 2. Channel Lookup                │
                             │    ensure_channel_exists()       │
                             └────────────────┬─────────────────┘
                                              │ Not Found ──► send_status(403, "<chan> :No such channel") -> RETURN
                                              │ Found
                                              ▼
                             ┌──────────────────────────────────┐
                             │ 3. Kicker Membership Check       │
                             │    ensure_channel_member()       │
                             └────────────────┬─────────────────┘
                                              │ Not Member ──► send_status(442, "<chan> :You're not on that channel") -> RETURN
                                              │ Member
                                              ▼
                             ┌──────────────────────────────────┐
                             │ 4. Kicker Operator Check         │
                             │    ensure_channel_operator()     │
                             └────────────────┬─────────────────┘
                                              │ Not Operator ──► send_status(482, "<chan> :You're not channel operator") -> RETURN
                                              │ Operator
                                              ▼
                             ┌──────────────────────────────────┐
                             │ 5. Target Nickname Lookup        │
                             │    get_client(target_nick)       │
                             └────────────────┬─────────────────┘
                                              │ Not Found ──► send_status(401, "<target> :No such nick/channel") -> RETURN
                                              │ Found
                                              ▼
                             ┌──────────────────────────────────┐
                             │ 6. Target Channel Membership     │
                             │    channel.has_member(target_fd) │
                             └────────────────┬─────────────────┘
                                              │ Not in Channel ──► send_status(441, "<target> <chan> :They aren't on that channel") -> RETURN
                                              │ In Channel
                                              ▼
                             ┌──────────────────────────────────┐
                             │ 7. Reason Extraction             │
                             │    default: client.get_nickname()│
                             │    if line contains " :":        │
                             │       reason = line.strAfter(" :")│
                             └────────────────┬─────────────────┘
                                              │
                                              ▼
                             ┌────────────────────────────────────────────────────────┐
                             │ 8. Broadcast & Removal                                 │
                             │    kick_msg = make_msg(client, "KICK", "<chan> <target>", reason)│
                             │    channel.broadcast(kick_msg)                         │
                             │    channel.remove_client_from_channel(target_fd)       │
                             │      ├─► remove_invited(target_fd)                     │
                             │      ├─► remove_operator(target_fd)                    │
                             │      ├─► remove_member(target_fd)                      │
                             │      └─► if (channel.empty()) server->remove_channel() │
                             └────────────────────────────────────────────────────────┘
```

---

## 2. Code Trace & State Transitions

### State Variables Involved:
- `Client::socket` (`int`): client file descriptor.
- `Client::nickname` (`Wire`): client nickname.
- `Client::is_registered` (`bool`): registration flag.
- `Channel::name` (`Wire`): channel name.
- `Channel::member_fds` (`Set<int>`): set of client socket FDs joined to channel.
- `Channel::operator_fds` (`Set<int>`): set of client socket FDs holding operator privilege (+o).
- `Channel::invited_fds` (`Set<int>`): set of client socket FDs holding pending invite (+i).
- `Server::channels` (`Map<Wire, Channel>`): table of active channels on server.
- `Server::clients` (`Map<int, Client>`): table of active client sessions.

### State Transitions Table for KICK:

| Initial State | Command Issued | Resulting State | Output / Numerics |
| :--- | :--- | :--- | :--- |
| `Kicker` unregistered | `KICK #chan target` | No change | `451 :You have not registered` |
| `Kicker` registered | `KICK` *(no params)* | No change | `461 KICK :Not enough parameters` |
| `Kicker` registered | `KICK #chan` *(1 param)* | No change | `461 KICK :Not enough parameters` |
| `Kicker` registered | `KICK #nonexistent target` | No change | `403 #nonexistent :No such channel` |
| `Kicker` not in `#chan` | `KICK #chan target` | No change | `442 #chan :You're not on that channel` |
| `Kicker` in `#chan`, not op | `KICK #chan target` | No change | `482 #chan :You're not channel operator` |
| `Kicker` op, `target` offline | `KICK #chan ghost` | No change | `401 ghost :No such nick/channel` |
| `Kicker` op, `target` online, not in `#chan` | `KICK #chan outsider` | No change | `441 outsider #chan :They aren't on that channel` |
| `Kicker` op, `target` member, with colon reason | `KICK #chan user :Bad conduct` | `target` removed from `#chan` | Broadcast: `:kicker!user@host KICK #chan user :Bad conduct` |
| `Kicker` op, `target` member, single-word reason | `KICK #chan user spammer` | `target` removed from `#chan` | **Bug**: Broadcasts `:kicker!user@host KICK #chan user :kicker` (`spammer` discarded!) |
| `Kicker` op, `target` member, no reason | `KICK #chan user` | `target` removed from `#chan` | Broadcast: `:kicker!user@host KICK #chan user :kicker` |
| `Kicker` op kicks **themselves** (sole member) | `KICK #chan kicker` | Channel emptied & deleted | Broadcast sent to kicker; channel removed from server |
| `Kicker` op kicks **themselves** (other members remain) | `KICK #chan kicker` | Kicker leaves channel; **channel becomes opless** | Broadcast to all; channel remains without any operators |
| `Kicker` op kicks **another op** | `KICK #chan other_op` | `other_op` stripped of op & membership | Broadcast to all; `other_op` removed from members and ops |

---

## 3. Deep Edge Case Matrix

### A. Input Parsing & Grammar Edge Cases

#### 1. Single-Word Reason Loss (Lack of Colon Prefix)
- **Code Reference**: `ServerChannelOps.cpp:99-101`
  ```cpp
  Wire reason = client.get_nickname();
  if (line.contains(" :"))
      reason = line.strAfter(" :");
  ```
- **RFC Standard (RFC 2812 §3.2.8)**: `KICK <channel> <user> *( "," <user> ) [<comment>]`. The comment can be provided as a regular single token without a leading colon, e.g. `KICK #chan target rulebreaker`.
- **Flaw**: The server strictly requires `" :"` to extract a reason. If `arguments.size() >= 3` and no colon was given, `line.contains(" :")` evaluates to false. The reason defaults to `client.get_nickname()`.
- **Impact**: Any single-word kick reason without a colon (e.g. `KICK #chan user spam`) is silently dropped and replaced with the operator's own nickname.

#### 2. Colon-Prefixed Target Parameter (`KICK #chan :target`)
- **Code Reference**: `ServerCommands.cpp:41`, `ServerChannelOps.cpp:73, 85`
  ```cpp
  const Wire &target_nick = arguments[1];
  Client &target = get_client(target_nick);
  ```
- **Grammar Issue**: IRC RFC 2812 allows the trailing parameter of any command to have a leading colon. When a client or bot sends `KICK #chan :target` (omitting a comment), `split_arguments` keeps `":target"` in `arguments[1]`.
- **Flaw**: `get_client(":target")` attempts to find a user whose nickname is literally `":target"`. Because `:` is invalid in nicknames (`is_valid_nickname`), the lookup always fails.
- **Impact**: Server responds with `401 :target :No such nick/channel` instead of kicking `target`.

#### 3. Premature Reason Splitting via `line.contains(" :")`
- **Code Reference**: `ServerChannelOps.cpp:100-101`
  ```cpp
  if (line.contains(" :"))
      reason = line.strAfter(" :");
  ```
- **Flaw**: `line.strAfter(" :")` searches for the first occurrence of `" :"` anywhere in the raw command line.
- **Scenario**: If a command line contains `" :"` prior to the reason parameter (e.g. `KICK #chan :target :real reason`), the reason will be sliced from the first `" :"`, including the target name.

#### 4. Lack of Multi-Channel and Multi-User Batch Kicks
- **RFC Standard (RFC 2812 §3.2.8)**: `KICK <channel>{,<channel>} <user>{,<user>} [<comment>]`.
- **Flaw**: `arguments[0]` and `arguments[1]` are parsed as literal strings without comma splitting.
- **Impact**: Batch kicks such as `KICK #chan u1,u2,u3 :cleanup` or `KICK #c1,#c2 u1 :massban` fail with `401 u1,u2,u3 :No such nick/channel` or `403 #c1,#c2 :No such channel`.

#### 5. Case-Sensitivity in Channel Name Lookup
- **Code Reference**: `Server.cpp:165-168`, `ServerChannelOps.cpp:27`
  ```cpp
  Channel &Server::get_channel(const Wire &name) {
      return (channels.fetch(name));
  }
  ```
- **RFC Standard (RFC 2812 §2.2)**: Channel names are case-insensitive ASCII strings.
- **Flaw**: `channels.fetch(name)` performs an exact, case-sensitive string comparison.
- **Impact**: If `#General` is created, issuing `KICK #general user` or `KICK #GENERAL user` fails with `403 #general :No such channel`.

#### 6. Case-Sensitivity in Target Nickname Lookup
- **Code Reference**: `Server.cpp:123-131`
  ```cpp
  static bool match_nickname(const Client &c, const Wire &nick) {
      return (c.get_nickname() == nick);
  }
  ```
- **RFC Standard (RFC 2812 §2.2)**: Nicknames are case-insensitive.
- **Flaw**: `match_nickname` checks `c.get_nickname() == nick` using case-sensitive comparison.
- **Impact**: If target is registered as `Alice`, issuing `KICK #chan alice` fails with `401 alice :No such nick/channel`.

---

### B. Access Control & Permission Edge Cases

#### 1. Unregistered Client Execution
- **Code Reference**: `ServerCommands.cpp:303-304`
  ```cpp
  else if (!client.get_register_status())
      send_status(client, "451", ":You have not registered");
  ```
- **Behavior**: An unregistered connection issuing `KICK #chan user` is immediately stopped and receives `451 :You have not registered`.

#### 2. Kicker is Not in Channel (Outside Kick Attempt)
- **Code Reference**: `ServerChannelOps.cpp:34-43`, `79-80`
  ```cpp
  if (!channel.has_member(client.get_socket())) {
      send_status(client, "442", channel.get_name() + " :You're not on that channel");
      return false;
  }
  ```
- **Behavior**: If an operator is not joined to the channel, kicking is denied with `442 <chan> :You're not on that channel`. Operators cannot kick from outside.

#### 3. Regular Member Attempting KICK (Non-Operator)
- **Code Reference**: `ServerChannelOps.cpp:46-55`, `81-82`
  ```cpp
  if (!channel.is_operator(client.get_socket())) {
      send_status(client, "482", channel.get_name() + " :You're not channel operator");
      return false;
  }
  ```
- **Behavior**: Non-operators receive `482 <chan> :You're not channel operator`.

#### 4. Target Not on Channel
- **Code Reference**: `ServerChannelOps.cpp:92-96`
  ```cpp
  if (!channel.has_member(target.get_socket())) {
      send_status(client, "441", Wire(target_nick, " ", channel_name, " :They aren't on that channel"));
      return ;
  }
  ```
- **Behavior**: If target client is connected to the server but not inside the given channel, server returns `441 <target> <chan> :They aren't on that channel`.

---

### C. Identity, Self-Kicking & Op-on-Op Edge Cases

#### 1. Self-Kick (Operator Kicks Themselves)
- **Scenario**: Operator executes `KICK #chan mynick :I quit`.
- **Execution Flow**:
  1. `ensure_channel_member` succeeds (operator is member).
  2. `ensure_channel_operator` succeeds (operator has op status).
  3. `get_client("mynick")` returns the operator.
  4. `channel.has_member(kicker_fd)` succeeds.
  5. `kick_msg` is constructed: `:mynick!user@host KICK #chan mynick :I quit`.
  6. `channel.broadcast(kick_msg)` sends message to all members in `#chan` (including the kicker).
  7. `channel.remove_client_from_channel(kicker_fd)` strips kicker's membership, op status, and invite status.
- **Consequences**:
  - **Case A: Kicker was the ONLY member**: `channel.empty()` evaluates to true -> `server->remove_channel(name)` deletes the channel from memory.
  - **Case B: Other members remain**: Kicker leaves. If kicker was the *only* operator, the channel is now **opless**. Remaining non-op members cannot assign new operators, kick, set modes, invite, or change topic (+t).

#### 2. Op-on-Op Kick (Operator Kicks Another Operator)
- **Scenario**: Op A executes `KICK #chan OpB :bye`.
- **Execution Flow**:
  - Op A has op status. Target Op B is in channel and has op status.
  - Broadcast notification is sent to everyone (including Op B).
  - `remove_client_from_channel(OpB_fd)` is called.
  - Op B is removed from `member_fds` and `operator_fds`.
- **RFC Compliance**: Under RFC 1459/2812, all channel operators are equal peers. Any operator can kick any other operator.

#### 3. Duplicate / Rapid Pipelined Kicks
- **Scenario**: Op A sends `KICK #chan target\r\nKICK #chan target\r\n` in a single TCP packet.
- **Execution Flow**:
  - Command 1: Succeeds. Target is removed from channel and notified.
  - Command 2: Fails at `channel.has_member(target.get_socket())`. Server returns `441 target #chan :They aren't on that channel`.

---

### D. Channel State, Modes & Lifecycle Edge Cases

#### 1. KICK from Invite-Only Channel (+i)
- **State Interaction**:
  - When user was originally invited via `INVITE` and joined, `let_client_join_channel` cleared their invite (`channel.remove_invited(fd)`).
  - When the user is kicked, `remove_client_from_channel` also calls `remove_invited(fd)`.
  - If `#chan` has mode `+i`, the kicked user **cannot** rejoin without receiving a fresh `INVITE`. Attempting to join produces `473 #chan :Cannot join channel (+i)`.

#### 2. KICK from User-Limit Channel (+l)
- **State Interaction**:
  - If a channel has mode `+l 2` and is currently full (2/2 members).
  - An operator kicks 1 member.
  - `member_fds.size()` drops to 1.
  - Now, any user (including the kicked user) can join since `members.size() < limit`.

#### 3. KICK from Key-Protected Channel (+k)
- **State Interaction**:
  - Kicking does not alter `channel_key` or `key_enabled`.
  - Kicked user can rejoin if they supply the correct key (`JOIN #chan secret`), unless blocked by `+i` or `+l`.

#### 4. KICK and Empty Channel Garbage Collection
- **Code Reference**: `Channel.cpp:123-125`
  ```cpp
  if (empty() && server)
      server->remove_channel(name);
  ```
- **Guarantees**: When the final member of a channel is kicked, the channel is immediately erased from `Server::channels`.
- **Re-creation**: A subsequent `JOIN #chan` will create a fresh channel instance with default modes (empty topic, no key, no limit, not invite-only) and grant operator status to the first joiner.

#### 5. Ghost FD Reuse Safety
- **Mechanism**: `remove_client_from_channel(fd)` removes `fd` from `invited_fds`, `operator_fds`, and `member_fds`.
- **Safety**: If the kicked client disconnects and the OS reallocates the same file descriptor to a newly connecting client, the new client has zero residual operator or invite privileges in `#chan`.

---

### E. Socket, Buffer & Pipelining Edge Cases

#### 1. Broadcast Timing & Kicked User Notification
- **Code Reference**: `ServerChannelOps.cpp:104-105`
  ```cpp
  channel.broadcast(kick_message);
  channel.remove_client_from_channel(target.get_socket());
  ```
- **Order of Execution**: `channel.broadcast` executes **BEFORE** `remove_client_from_channel`.
- **Correctness**: The target user is still in `member_fds` when `broadcast` runs, guaranteeing that the target receives their own KICK notification before being removed from the channel.

#### 2. SendQ Overflow During Kick Broadcast
- **Code Reference**: `ServerLoop.cpp:117-121`, `ServerMessaging.cpp:30-38`
  - If a channel member's output buffer exceeds `MAX_OUTPUT_BUFFER_SIZE` during the KICK broadcast, `send_to_client` immediately triggers `disconnect_client(fd)`.
  - `Channel::broadcast` iterates over a copy/snapshot of `member_fds`, preventing iterator invalidation even if a slow recipient is disconnected mid-broadcast.

#### 3. Client Line Buffer Limit (510 Chars)
- **Code Reference**: `ServerLoop.cpp:22-31`, `168-172`
- **Behavior**: If an operator sends a giant KICK command or multi-line flood exceeding 510 characters before `\r\n`, `input_exceeds_irc_line_limit` catches it and disconnects the flooding client.

---

## 4. Command Interactions

### 1. KICK + JOIN / PART / NAMES

```
Op:      KICK #chan UserA :bye
Server:  (Removes UserA from #chan)
UserA:   PRIVMSG #chan :still here?
Server:  442 #chan :You're not on that channel
UserA:   PART #chan
Server:  442 #chan :You're not on that channel
UserB:   NAMES #chan
Server:  353 = #chan :@Op UserB   <-- UserA is omitted
Server:  366 #chan :End of /NAMES list
UserA:   JOIN #chan
Server:  (If public, UserA rejoins as normal member)
```

- **PART after KICK**: When a kicked user sends `PART #chan`, the server returns `442 <chan> :You're not on that channel`.
- **NAMES after KICK**: `send_channel_names_reply` only lists active `member_fds`. The kicked client is immediately absent from subsequent `353 RPL_NAMREPLY` responses.

---

### 2. KICK + MODE (+o, -o, +i, +k, +l)

- **KICK after De-opping Kicker (`MODE #chan -o kicker`)**:
  If the operator demotes themselves before executing KICK, `ensure_channel_operator` returns `482 <chan> :You're not channel operator`.
- **Kicking an Operator (`KICK #chan other_op`)**:
  The kicked operator is cleanly removed from both `member_fds` and `operator_fds`. If they later rejoin, they rejoin as a regular member without operator privileges.
- **KICK in `+i` (Invite-Only) Channel**:
  Kicked user cannot rejoin via `JOIN #chan` unless an operator sends `INVITE <user> #chan`.
- **KICK in `+l` (User Limit) Channel**:
  Kicking a user decrements the channel occupant count, freeing a slot for new clients to join.

---

### 3. KICK + INVITE

- **Re-inviting Kicked User**:
  An operator can kick a disruptive user and later issue `INVITE <user> #chan`.
  `handle_invite` checks `channel.has_member(target)` (which is now false), adds target to `invited_fds`, and sends the INVITE notice.
  The target can then successfully rejoin even if `#chan` is `+i`.

---

### 4. KICK + TOPIC

- **Topic Viewing / Setting after KICK**:
  Once kicked, the user cannot execute `TOPIC #chan :new topic` (fails with `442 :You're not on that channel`).
- **Channel Topic Retention**:
  Kicking members (even operators) does not alter or erase the channel's current topic. The topic persists until the channel is empty and destroyed.

---

### 5. KICK + PRIVMSG / NOTICE

- **Channel Message Rejection**:
  Immediately after being kicked, any `PRIVMSG #chan :text` sent by the kicked client fails with `442 <chan> :You're not on that channel`.
- **Direct Messages (User-to-User)**:
  Direct `PRIVMSG <kicker> :Why did you kick me?` remains functional because KICK only alters channel membership, not global connection status.

---

### 6. KICK + NICK Collision / Nick Changes

- **Target Changes Nick Before KICK Processed**:
  If Target sends `NICK NewNick` and Op sends `KICK #chan OldNick` in the same processing cycle:
  If `NICK` is processed first, `OldNick` no longer exists. `get_client("OldNick")` fails with `401 OldNick :No such nick/channel`.
- **Audience Recalculation**:
  When a kicked user later changes nickname via `NICK NewNick`, `Server::get_client_audience` calculates recipients based on mutual channels. Members of `#chan` will not receive the NICK broadcast (unless they share other mutual channels with the kicked user).

---

### 7. KICK + QUIT / Unexpected Disconnection / SendQ Overflow

- **Target Quits Before KICK Processed**:
  If target socket closes or sends `QUIT`, `disconnect_client` removes them from all channels and `Server::clients`.
  When `KICK #chan target` runs, `get_client("target")` fails with `401 target :No such nick/channel`.
- **Kicker Quits After Kicking**:
  If kicker kicks all other members and then quits, channel cleanup occurs smoothly without leaking memory or leaving dangling pointers.

---

## 5. Summary of Identified Vulnerabilities & Failure Modes

| # | Flaw / Edge Case | File & Lines | Severity | Impact / Symptoms |
| :- | :--- | :--- | :--- | :--- |
| **1** | **Single-word reason loss without colon** | `ServerChannelOps.cpp:99-101` | **Medium** | `KICK #c user spam` broadcasts `:kicker KICK #c user :kicker`. The reason `spam` is silently replaced. |
| **2** | **Colon-prefixed target nick failure** | `ServerChannelOps.cpp:73, 85` | **Medium** | `KICK #c :user` sends `401 :user :No such nick/channel` due to unstripped leading colon. |
| **3** | **Case-sensitive channel lookup** | `Server.cpp:165-168` | **Medium** | `KICK #CHAN user` fails with `403 #CHAN :No such channel` if created as `#chan`. |
| **4** | **Case-sensitive target nick lookup** | `Server.cpp:123-131` | **Medium** | `KICK #chan ALICE` fails with `401 ALICE :No such nick/channel` if registered as `Alice`. |
| **5** | **No multi-channel or multi-user batch kicks** | `ServerChannelOps.cpp:64-74` | **Low** | Batch kicks like `KICK #c u1,u2` fail with `401 u1,u2 :No such nick/channel`. |
| **6** | **Permanent Opless Channel on Self-Kick** | `ServerChannelOps.cpp:105` | **Low (RFC Standard)** | If the only operator kicks themselves while other members remain, channel permanently loses operator management. |
| **7** | **Premature reason extraction on `" :"`** | `ServerChannelOps.cpp:100-101` | **Low** | Slicing reason using `line.strAfter(" :")` can split on earlier parameters if they contain `" :"`. |
| **8** | **Colon prefix on channel parameter (`:#chan`)** | `ServerChannelOps.cpp:72, 76` | **Low** | `KICK :#chan user` fails with `403 :#chan :No such channel`. |

---

## 6. Automated Regression & Vulnerability Test Suite (`tester/scenarios/commands/`)

The following test scenario files have been created to verify RFC compliance and capture edge cases / vulnerabilities:

| Spec File | Test Focus & Verification | Expected Behavior | Buggy Behavior (Fails Test) |
| :--- | :--- | :--- | :--- |
| `60_KICK_not_registered_error.spec` | Registration gate | `451 :You have not registered` | Command executed prematurely |
| `61_KICK_missing_params.spec` | Parameter count validation (< 2 args) | `461 KICK :Not enough parameters` | Undefined behavior / crash |
| `62_KICK_nonexistent_channel.spec` | Nonexistent channel lookup | `403 <chan> :No such channel` | State leak or crash |
| `63_KICK_kicker_not_on_channel.spec` | Kicker membership requirement | `442 <chan> :You're not on that channel` | Outside kick permitted |
| `64_KICK_kicker_not_channel_operator.spec` | Operator privilege enforcement (+o) | `482 <chan> :You're not channel operator` | Regular members can kick ops |
| `65_KICK_target_not_found.spec` | Offline / nonexistent target lookup | `401 <target> :No such nick/channel` | Null dereference |
| `66_KICK_target_not_on_channel.spec` | Target channel membership validation | `441 <target> <chan> :They aren't on that channel` | Target kicked without being in channel |
| `67_KICK_success_with_colon_reason.spec` | Standard KICK with comment broadcast | Broadcast `:kicker KICK #chan target :reason` to all; target evicted | Notification dropped |
| `68_KICK_single_word_reason_without_colon.spec` | Single-word reason without leading colon | Broadcast comment `:spammer` | **BUG**: Reason dropped, replaced with kicker nick |
| `69_KICK_colon_prefix_on_target.spec` | Trailing colon on target argument (`:target`) | Strips colon, kicks target | **BUG**: Returns `401 :target :No such nick/channel` |
| `70_KICK_case_insensitive_channel.spec` | Case-insensitive channel matching | `#SecretLobby` matched by `#secretlobby` | **BUG**: Returns `403 #secretlobby :No such channel` |
| `71_KICK_case_insensitive_target_nick.spec` | Case-insensitive target nick matching | `Bob` matched by `BOB` | **BUG**: Returns `401 BOB :No such nick/channel` |
| `72_KICK_self_kick_last_member_channel_destroyed.spec` | Sole member self-kick channel GC | Channel destroyed; new join creates fresh op | Channel leaked / zombie state |
| `73_KICK_self_kick_opless_channel.spec` | Self-kick with remaining members | Channel becomes opless; non-ops cannot execute op commands | Privileges escalated or crash |
| `74_KICK_op_on_op.spec` | Operator kicking another operator | Target loses op & membership; rejoin is non-op | Target retains op |
| `75_KICK_invite_only_rejoin_blocked.spec` | Invite status cleared on kick (+i) | `473 :Cannot join channel (+i)` on rejoin | Rejoining permitted without new invite |
| `76_KICK_user_limit_slot_freed.spec` | Capacity freed on kick (+l) | Waiting user can join immediately after kick | Channel reports full incorrectly |
| `77_KICK_multi_target_batch.spec` | Batch comma-separated target kicks | Both targets kicked | **BUG**: Returns `401 Bob,Charlie :No such nick/channel` |
| `78_KICK_post_kick_privmsg_rejected.spec` | Post-kick channel interaction rejection | `442 <chan> :You're not on that channel` | Target still broadcasts to channel |
| `79_KICK_ghost_fd_reuse.spec` | Operator FD cleanup & no ghost op | Reconnected socket has no residual operator status | New client inherits operator status |
| `80_KICK_colon_channel_prefix.spec` | Colon-prefixed channel name (`:#lobby`) | Strips colon, kicks target | **BUG**: Returns `403 :#lobby :No such channel` |
| `81_KICK_ampersand_channel.spec` | Local channel prefix support (`&chan`) | KICK executed on local channel | Channel rejected |
| `82_KICK_empty_reason_colon_only.spec` | Empty colon reason (`KICK #chan target :`) | Clean KICK broadcast without trailing colon or empty | Formatting corrupts IRC stream |
| `83_KICK_names_reply_exclusion.spec` | Names list update post-kick | 353 RPL_NAMREPLY excludes kicked client | Ghost names in RPL_NAMREPLY |

---
