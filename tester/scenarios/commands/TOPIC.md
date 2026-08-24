# Detailed TOPIC Command Analysis: Lifecycle, Edge Cases & Interactions

A comprehensive, line-by-line audit of the `TOPIC` command implementation in `ft_irc` across the entire codebase (`ServerChannelOps.cpp`, `ServerCommands.cpp`, `ServerMessaging.cpp`, `ServerHelper.cpp`, `ServerLoop.cpp`, `Channel.cpp`, `Channel.hpp`, `Client.cpp`, and `Wire.hpp`).

---

## Table of Contents
1. [End-to-End Flow Diagram](#1-end-to-end-flow-diagram)
2. [Code Trace & State Transitions](#2-code-trace--state-transitions)
3. [Deep Edge Case Matrix](#3-deep-edge-case-matrix)
   - [A. Input Parsing & Parameter Grammar Edge Cases](#a-input-parsing--parameter-grammar-edge-cases)
   - [B. Permission & Channel State Edge Cases](#b-permission--channel-state-edge-cases)
   - [C. Topic Setting, Clearing & Querying Edge Cases](#c-topic-setting-clearing--querying-edge-cases)
   - [D. Broadcasting & Message Delivery Edge Cases](#d-broadcasting--message-delivery-edge-cases)
4. [Command Interactions (What Happens When TOPIC Interacts With...)](#4-command-interactions)
   - [1. TOPIC + JOIN (Missing RPL_TOPIC on Channel Join)](#1-topic--join-missing-rpl_topic-on-channel-join)
   - [2. TOPIC + MODE (+t / -t Topic Restrictions)](#2-topic--mode-t---t-topic-restrictions)
   - [3. TOPIC + MODE (+o / -o Operator Privilege Transitions)](#3-topic--mode-o---o-operator-privilege-transitions)
   - [4. TOPIC + PART / KICK / Channel Destruction](#4-topic--part--kick--channel-destruction)
   - [5. TOPIC + NICK (Broadcaster Identity)](#5-topic--nick-broadcaster-identity)
   - [6. TOPIC + INVITE & Access Restrictions (+i, +k, +l)](#6-topic--invite--access-restrictions-i-k-l)
   - [7. TOPIC + QUIT / Socket Disconnect & Buffer Flushing](#7-topic--quit--socket-disconnect--buffer-flushing)
5. [Summary of Critical Vulnerabilities & Recommended Fixes](#5-summary-of-critical-vulnerabilities--recommended-fixes)

---

## 1. End-to-End Flow Diagram

```
[ TCP Inbound Packet: "TOPIC #chan :New Topic\r\n" or "TOPIC #chan\r\n" ]
         │
         ▼
[ ServerLoop.cpp: handle_client_input(fd) ]
   - Reads TCP bytes into client.buffer
   - Validates line length (<= 510 chars before \r\n)
         │
         ▼
[ ServerCommands.cpp: handle_line(client, pos) ]
   - Slices line, erases "\r\n" from client.buffer
   - Extracts command: line.splitBy(' ')[0].toUpper() -> "TOPIC"
   - Calls split_arguments(line) -> ["#chan", ":New", "Topic"]
   - Calls dispatch_command(client, "TOPIC", line, arguments)
         │
         ▼
[ ServerCommands.cpp: dispatch_command ]
   - Checks client.get_register_status()
   - If false: send_status(client, "451", ":You have not registered") -> RETURN
   - If true: calls handle_topic(client, line, arguments)
         │
         ▼
[ ServerChannelOps.cpp: handle_topic(client, line, arguments) ]
   │
   ├─► 1. Parameter Count Guard: arguments.size() < 1
   │        └─► YES: send_status(client, "461", "TOPIC :Not enough parameters") -> RETURN
   │
   ├─► 2. Channel Existence Guard: ensure_channel_exists(client, channel_name)
   │        └─► NOT FOUND: send_status(client, "403", channel_name + " :No such channel") -> RETURN
   │
   ├─► 3. Channel Membership Guard: ensure_channel_member(client, channel)
   │        └─► NOT MEMBER: send_status(client, "442", channel_name + " :You're not on that channel") -> RETURN
   │
   ├─► 4. Query Mode vs Set Mode Branch: !line.contains(" :")
   │        │
   │        ├─► [QUERY MODE] (No " :" in raw line):
   │        │        ├─► If channel.get_topic().empty():
   │        │        │        send_status(client, "331", channel_name + " :No topic is set") -> RETURN
   │        │        └─► Else:
   │        │                 send_status(client, "332", channel_name + " :" + topic) -> RETURN
   │        │
   │        └─► [SET / CLEAR MODE] (" :" found in raw line):
   │                 │
   │                 ├─► 5. Topic Restriction Check (+t):
   │                 │        If channel.is_topic_restricted() && !channel.is_operator(client.get_socket()):
   │                 │             send_status(client, "482", channel_name + " :You're not channel operator") -> RETURN
   │                 │
   │                 ├─► 6. Extract New Topic:
   │                 │        new_topic = line.strAfter(" :")
   │                 │
   │                 ├─► 7. Mutate State:
   │                 │        channel.set_topic(new_topic)
   │                 │
   │                 └─► 8. Channel Broadcast:
   │                          channel.broadcast(client, "TOPIC", new_topic)
   │                          (Sends ":nick!user@localhost TOPIC #chan :new_topic\r\n" to all channel members including sender)
```

---

## 2. Code Trace & State Transitions

### State Variables Involved:
- `Channel::topic` (`Wire`): Stored topic string for the channel (default: `""`).
- `Channel::topic_restricted` (`bool`): `+t` flag indicating if topic changes require channel operator privileges (default: `false`).
- `Channel::member_fds` (`Set<int>`): Set of active member socket FDs.
- `Channel::operator_fds` (`Set<int>`): Set of channel operator socket FDs.
- `Client::is_registered` (`bool`): Registration status (must be `true` to invoke TOPIC).

### State Transitions Table:

| Current Channel State | Client Privileges | TOPIC Input | Resulting State | Numeric Reply / Broadcast Message |
| :--- | :--- | :--- | :--- | :--- |
| Unregistered client | Any | `TOPIC #chan` | Unchanged | `451 :You have not registered` |
| `topic=""`, `+t` or `-t` | Non-member | `TOPIC #chan` | Unchanged | `442 #chan :You're not on that channel` |
| Channel does not exist | Registered | `TOPIC #ghost` | Unchanged | `403 #ghost :No such channel` |
| `topic=""`, `+t` or `-t` | Member (any) | `TOPIC #chan` | Unchanged | `331 #chan :No topic is set` |
| `topic="Alpha"`, `+t` or `-t` | Member (any) | `TOPIC #chan` | Unchanged | `332 #chan :Alpha` |
| `topic="Alpha"`, `-t` (unrestricted) | Regular member | `TOPIC #chan :Beta` | `topic="Beta"` | Broadcast: `:nick!user@localhost TOPIC #chan :Beta` |
| `topic="Alpha"`, `+t` (restricted) | Regular member | `TOPIC #chan :Beta` | `topic="Alpha"` (unchanged) | `482 #chan :You're not channel operator` |
| `topic="Alpha"`, `+t` (restricted) | Operator (`@`) | `TOPIC #chan :Beta` | `topic="Beta"` | Broadcast: `:nick!user@localhost TOPIC #chan :Beta` |
| `topic="Alpha"`, `-t` (unrestricted) | Regular member | `TOPIC #chan :` | `topic=""` (cleared) | Broadcast: `:nick!user@localhost TOPIC #chan :` |
| `topic="Alpha"`, `+t` (restricted) | Regular member | `TOPIC #chan :` | `topic="Alpha"` (unchanged) | `482 #chan :You're not channel operator` |
| `topic="Alpha"`, `+t` (restricted) | Operator (`@`) | `TOPIC #chan :` | `topic=""` (cleared) | Broadcast: `:nick!user@localhost TOPIC #chan :` |

---

## 3. Deep Edge Case Matrix

### A. Input Parsing & Parameter Grammar Edge Cases

| ID | Scenario / Input | Expected RFC 2812 Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A1** | **Single-word topic without colon** (`TOPIC #chan Alpha`) | Sets topic to `"Alpha"` and broadcasts | **Treated as query `TOPIC #chan`**; returns `331` or `332` | **CRITICAL** | `handle_topic` checks `!line.contains(" :")` to distinguish query from set. If no colon precedes parameter, server fails to recognize a topic update. |
| **A2** | **Multi-word topic without colon** (`TOPIC #chan Alpha Beta`) | RFC allows single token or trailing colon; sets topic or errors | **Treated as query `TOPIC #chan`**; `Alpha` & `Beta` ignored | **HIGH** | `!line.contains(" :")` branch evaluates to `true`; server ignores all parameters after `#chan`. |
| **A3** | **Colon-prefixed channel name** (`TOPIC :#chan`) | Resolves channel `#chan` and queries topic | **Fails with `403 :#chan :No such channel`** | **MEDIUM** | `split_arguments` does not strip leading colons from non-trailing parameters. `get_channel(":#chan")` lookup fails. |
| **A4** | **Colon-prefixed channel name with topic** (`TOPIC :#chan :New Topic`) | Sets topic of `#chan` to `"New Topic"` | Look up `":#chan"` -> `403 :#chan :No such channel` | **MEDIUM** | Same as A3. Common in some automated IRC scripts and bridges. |
| **A5** | **Empty trailing colon** (`TOPIC #chan :`) | Clears channel topic (`topic = ""`) | Clears topic to `""` and broadcasts empty topic `:nick!user@host TOPIC #chan :` | **OK** | `line.strAfter(" :")` evaluates to `""`, properly clearing topic. |
| **A6** | **Single whitespace topic** (`TOPIC #chan : `) | Topic set to string with single space `" "` | Topic set to `" "`; not treated as empty | **LOW** | `channel.get_topic().empty()` is `false`, query returns `332 #chan : `. |
| **A7** | **Multiple spaces before colon** (`TOPIC #chan  :Hello`) | Sets topic to `"Hello"` | `line.strAfter(" :")` splits on first `" :"`, which starts at index of 2nd space; topic becomes `"Hello"` | **OK** | Preserved properly because `strAfter` extracts everything after the `" :"` delimiter. |
| **A8** | **Leading space inside topic** (`TOPIC #chan : Hello World`) | Sets topic to `" Hello World"` (leading space preserved) | `line.strAfter(" :")` returns `" Hello World"` | **OK** | Compliant with RFC trailing parameter semantics. |
| **A9** | **Internal colons in topic** (`TOPIC #chan :Part 1: Intro : Extra`) | Sets topic to `"Part 1: Intro : Extra"` | `strAfter(" :")` splits at the FIRST `" :"`, preserving internal colons | **OK** | Handled correctly. |
| **A10** | **No arguments** (`TOPIC` or `TOPIC\r\n`) | `461 ERR_NEEDMOREPARAMS` | Sends `461 TOPIC :Not enough parameters` | **OK** | Handled via `arguments.size() < 1`. |
| **A11** | **Topic string exceeding IRC buffer size** | Topic clamped/truncated to fit in 512-byte IRC message | Allowed up to input line limit (~510); when prepended with `:nick!user@host TOPIC #chan :`, outgoing message may exceed 512 bytes | **HIGH** | Outgoing line can be up to 570+ bytes. Standard strict IRC clients (e.g. HexChat/Irssi) may drop or truncate message. |

---

### B. Permission & Channel State Edge Cases

| ID | Scenario | Expected Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B1** | **Querying topic from outside channel** (`TOPIC #chan` when client is not joined) | RFC 2812 §3.2.4 lists `442 ERR_NOTONCHANNEL` as possible numeric reply | Returns `442 #chan :You're not on that channel` | **OK** | Compliant with RFC 2812 §3.2.4 (`ensure_channel_member` returns 442). |
| **B2** | **Setting topic when channel is unrestricted (`-t`)** | Any regular member can set/clear topic | Allowed for all channel members | **OK** | Checks `channel.is_topic_restricted()` (which is `false`), allows non-ops. |
| **B3** | **Setting topic when channel is restricted (`+t`) as non-op** | Rejected with `482 ERR_CHANOPRIVSNEEDED` | Returns `482 #chan :You're not channel operator` | **OK** | Topic remains unchanged. |
| **B4** | **Querying topic when channel is restricted (`+t`) as non-op** | Allowed! Returns current topic `331` / `332` | Returns `331` or `332` successfully | **OK** | Query branch executes before `+t` operator check. |
| **B5** | **Zero Operators Remaining in `+t` channel** (sole op parts/quits) | Regular members cannot change topic under `+t` | Returns `482` for all remaining regular members | **OK / DESIGN** | Topic is permanently locked until channel becomes empty or server admin intervenes. |
| **B6** | **Unregistered Client sends TOPIC** | `451 ERR_NOTREGISTERED` | Returns `451 :You have not registered` | **OK** | Handled in `dispatch_command`. |

---

### C. Topic Setting, Clearing & Querying Edge Cases

| ID | Scenario | Expected Behavior | Current Code Behavior | Severity | Detailed Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | **Clearing Topic (`TOPIC #chan :`)** | `Channel::topic` set to `""`; broadcast sent; query returns `331` | Sets `topic = ""`; broadcasts `:nick!user@host TOPIC #chan :`; query returns `331 #chan :No topic is set` | **OK** | Handled cleanly in `make_msg` (`cmd == "TOPIC"` special case). |
| **C2** | **Setting Identical Topic** (re-setting current topic) | Broadcasts topic change to channel | Broadcasts topic change to all members | **OK** | IRC servers broadcast even if topic string is identical. |
| **C3** | **Topic Query Response Format** | `331 <nick> <chan> :No topic is set`<br>`332 <nick> <chan> :<topic>` | Sends `331/332` with `:localhost 331/332 <nick> <chan> :<topic>` | **OK** | Matches RFC format. |
| **C4** | **Case Sensitivity in Channel Name Query** (`TOPIC #CHAN` vs `#chan`) | Channel names are case-insensitive per RFC 2812 | `get_channel("#CHAN")` is case-sensitive; returns `403 #CHAN :No such channel` | **HIGH** | `ChannelMap` is `Map<Wire, Channel>` with case-sensitive keys. |
| **C5** | **Special Formatting / Color Codes in Topic** (e.g. `\x0304Red\x03 \x02Bold\x02`) | Binary-safe propagation to all members | `Wire` string is binary-safe; colors and bold formatting preserved | **OK** | Standard mIRC/IRC formatting codes pass through unmodified. |

---

### D. Broadcasting & Message Delivery Edge Cases

| ID | Scenario | Expected Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **D1** | **Sender Broadcast Echo** | Sender must receive the `TOPIC` broadcast message to confirm update | `channel.broadcast(client, "TOPIC", new_topic)` sends to `member_fds` (all members including sender) | **OK** | Standard IRC broadcast pattern. |
| **D2** | **Single Member Channel Broadcast** | Only sender in channel -> only sender receives `TOPIC` message | Sender receives broadcast, output buffer flushed | **OK** | Handled properly. |
| **D3** | **Slow Client in Channel (SendQ Overflow during Broadcast)** | Slow client's output buffer fills up; server does not crash | `send_to_client` checks `MAX_OUTPUT_BUFFER_SIZE` (1 MB); disconnects slow client without corrupting iteration | **OK** | `broadcast` iterates temporary snapshot of FDs; non-fatal. |

---

## 4. Command Interactions

### 1. TOPIC + JOIN (Missing RPL_TOPIC on Channel Join)

```
[ Client A creates #channel and sets TOPIC #channel :Meeting at 5pm ]
                                │
[ Client B sends: JOIN #channel ]
                                │
                                ▼
[ Server: let_client_join_channel(chan, client, key) ]
   ├─► 1. Adds Client B to member_fds
   ├─► 2. Broadcasts ":ClientB!user@host JOIN #channel" to all members
   ├─► 3. Calls send_channel_names_reply(client, channel_name)
   │        ├─► Sends 353 RPL_NAMREPLY (member list)
   │        └─► Sends 366 RPL_ENDOFNAMES
   │
   └─► MISSING: Does NOT send 332 RPL_TOPIC or 331 RPL_NOTOPIC!
```

- **RFC 2812 Requirement (§3.2.1)**:
  > "If a JOIN is successful, the user is then sent the channel's topic (using RPL_TOPIC) and the list of users who are on the channel (using RPL_NAMREPLY), which MUST include the user."
- **Current Behavior**:
  `let_client_join_channel` only sends `353` and `366`. Newly joined users **never** receive the current channel topic on join unless they manually type `/TOPIC #channel`.
- **Severity**: **HIGH** (IRC client UI inconsistency; channel topic bar remains blank in HexChat/Irssi/WeeChat upon joining).

---

### 2. TOPIC + MODE (+t / -t Topic Restrictions)

- **Default State**: Channels are created with `topic_restricted = false` (`-t`). Any joined user can set or clear the topic.
- **Mode Toggle `+t`**:
  - `MODE #chan +t` sets `topic_restricted = true`.
  - Non-operators trying to change or clear topic receive `482 #chan :You're not channel operator`.
  - Non-operators can still query the topic with `TOPIC #chan` (receives `331` or `332`).
- **Mode Toggle `-t`**:
  - `MODE #chan -t` sets `topic_restricted = false`.
  - Regular members immediately regain ability to change/clear topic.
- **Querying Channel Modes (`MODE #chan`)**:
  - `send_channel_modes_reply` includes `t` in `324 RPL_CHANNELMODEIS` if `channel.is_topic_restricted()` is `true`.

---

### 3. TOPIC + MODE (+o / -o Operator Privilege Transitions)

- **Granting Op (`MODE #chan +o Bob`)**:
  - `Bob`'s socket FD is added to `Channel::operator_fds`.
  - `Bob` can now execute `TOPIC #chan :New Topic` even under `+t`.
- **Revoking Op (`MODE #chan -o Bob`)**:
  - `Bob`'s socket FD is removed from `Channel::operator_fds`.
  - If `+t` is active, subsequent `TOPIC #chan :New Topic` by `Bob` is rejected with `482`.
- **Topic Persistence Across De-Op**:
  - The topic set by `Bob` while he was operator remains active after `Bob` is de-opped (`-o`).

---

### 4. TOPIC + PART / KICK / Channel Destruction

- **Topic Persistence Across Member Leaves**:
  - As long as at least 1 member remains in the channel, the topic is completely preserved in `Channel::topic`.
  - A user who parted and rejoined can query `TOPIC #chan` and see the preserved topic.
- **Channel Destruction on Empty (`empty() == true`)**:
  - When the last member parts (`PART`), is kicked (`KICK`), or disconnects (`QUIT`/socket close):
    ```cpp
    void Channel::remove_client_from_channel(int client_fd) {
        remove_invited(client_fd);
        remove_operator(client_fd);
        remove_member(client_fd);
        if (empty() && server)
            server->remove_channel(name);
    }
    ```
  - The `Channel` instance is erased from `Server::channels`.
  - **Result**: The topic and `+t` mode are wiped. If a client joins `#chan` later, it is created anew with an empty topic and default modes.

---

### 5. TOPIC + NICK (Broadcaster Identity)

- **Broadcaster Prefix**:
  - `channel.broadcast(client, "TOPIC", new_topic)` invokes:
    ```cpp
    make_msg(client, "TOPIC", name, param);
    ```
  - `make_msg` reads `client.get_nickname()` dynamically.
- **Nick Change Before Topic**:
  - If `Alice` renames to `Alicia` (`NICK Alicia`), subsequent topic change is broadcast as:
    `:Alicia!user@localhost TOPIC #chan :New Topic`
  - All channel members see the updated nickname.

---

### 6. TOPIC + INVITE & Access Restrictions (+i, +k, +l)

- **Invited User Pre-Join**:
  - An invited user is in `invited_fds`, but NOT `member_fds`.
  - If invited user sends `TOPIC #chan` before joining, `ensure_channel_member` fails with `442 #chan :You're not on that channel`.
  - Invited users cannot peek at the channel topic before actually joining.
- **Key (+k) / Limit (+l) Protected Channels**:
  - Users outside the channel cannot query `TOPIC #chan` regardless of channel key or user limit (blocked by `442`).

---

### 7. TOPIC + QUIT / Socket Disconnect & Buffer Flushing

- **Pipelined TOPIC + QUIT**:
  - If an operator sends `TOPIC #chan :Final words\r\nQUIT :Bye\r\n` in a single TCP packet:
    1. `TOPIC` executes -> topic is stored -> broadcast message is buffered into the output buffers of all channel members.
    2. `QUIT` executes -> QUIT message is buffered -> client marked `_should_disconnect = true`.
    3. Event loop drains buffers to all peers before closing connections.
  - All channel members receive both the `TOPIC` change and the `QUIT` notification in the exact order they were sent.

---

## 5. Summary of Critical Vulnerabilities & Recommended Fixes

### 1. Topic Setting without Colon (Issue A1)
- **Bug**: `TOPIC #chan SingleWord` is treated as a query `TOPIC #chan` because `!line.contains(" :")` is checked.
- **Fix**: Check `arguments.size() >= 2` OR `line.contains(" :")` to detect topic set mode:
  ```cpp
  bool is_setting_topic = line.contains(" :") || arguments.size() > 1;
  if (!is_setting_topic)
  {
      // Query topic (331 / 332)
      ...
      return ;
  }

  // Extract new topic
  Wire new_topic;
  if (line.contains(" :"))
      new_topic = line.strAfter(" :");
  else
      new_topic = arguments[1];
  ```

---

### 2. Missing RPL_TOPIC on Channel Join (Interaction #1)
- **Bug**: When a client joins a channel, `let_client_join_channel` does not send `332 RPL_TOPIC` (or `331 RPL_NOTOPIC`).
- **Fix**: In `Server::let_client_join_channel`, send topic numeric reply before/after names reply:
  ```cpp
  if (!channel.get_topic().empty())
      send_status(client, "332", channel_name + " :" + channel.get_topic());
  else
      send_status(client, "331", channel_name + " :No topic is set");
  ```

---

### 3. Leading Colon in Channel Name (Issues A3, A4)
- **Bug**: `TOPIC :#chan` or `TOPIC :#chan :topic` causes channel lookup for `":#chan"`, returning `403 :No such channel`.
- **Fix**: Strip leading colon from channel name if present:
  ```cpp
  Wire channel_name = arguments[0];
  if (!channel_name.empty() && channel_name[0] == ':')
      channel_name = channel_name.substr(1);
  ```

---

### 4. Case-Insensitive Channel Lookups (Issue C4)
- **Bug**: `TOPIC #CHAN` fails if the channel was joined as `#chan`.
- **Fix**: Normalize channel names to lowercase in `get_channel` and `create_new_channel` (or use case-insensitive channel map lookup).

---

### 5. Maximum Topic Length Safeguard (Issue A11)
- **Bug**: Very long topic strings (~480 chars) cause outgoing broadcast lines `:nick!user@host TOPIC #chan :<topic>\r\n` to exceed the 512-byte IRC protocol limit.
- **Fix**: Clamp `new_topic` to a safe maximum length (e.g. 300-390 bytes) before storing and broadcasting:
  ```cpp
  if (new_topic.length() > 390)
      new_topic = new_topic.substr(0, 390);
  ```
