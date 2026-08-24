# Comprehensive MODE Command Flow & Edge Case Analysis

This document provides an exhaustive, line-by-line analysis of the `MODE` command lifecycle in `ft_irc`. It details input grammar edge cases, state transitions, security vulnerabilities, command interactions, channel state consequences, parameter processing quirks, and reachable failure modes.

---

## 1. Flow Overview & Architecture

### High-Level Architecture Diagram
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
!client.get_register_status()                command == "MODE"
        │                                           │
        ▼                                           ▼
send_status(451,                            Server::handle_mode
":You have not registered")                         │
                                                    ▼
                                    arguments.empty()? ──Yes──► send_status(461, "MODE :Not enough parameters")
                                                    │ No
                                                    ▼
                                    channel_name = arguments[0]
                                    channel_name.empty() || channel_name[0] != '#'? ──Yes──► (Silent return / Ignored)
                                                    │ No
                                                    ▼
                                    ensure_channel_exists(client, channel_name)
                                    Channel exists in server? ──No──► send_status(403, "<chan> :No such channel")
                                                    │ Yes
                                                    ▼
                                    ensure_channel_member(client, channel)
                                    Is client in channel? ──No──► send_status(442, "<chan> :You're not on that channel")
                                                    │ Yes
                                                    ▼
                                    arguments.size() == 1? ──Yes──► send_channel_modes_reply(client, channel) [RPL_CHANNELMODEIS 324]
                                                    │ No
                                                    ▼
                                    mode_string = arguments[1]
                                    mode_string == "b" || "+b"? ──Yes──► send_status(368, "<chan> :End of Channel Ban List")
                                                    │ No
                                                    ▼
                                    ensure_channel_operator(client, channel)
                                    Is client an operator? ──No──► send_status(482, "<chan> :You're not channel operator")
                                                    │ Yes
                                                    ▼
                                    count_required_mode_parameters(mode_string)
                                    arguments.size() < 2 + required_params? ──Yes──► send_status(461, "MODE :Not enough parameters")
                                                    │ No
                                                    ▼
                                    Loop over mode_string characters:
                                      - '+', '-' : update sign
                                      - sign == 0 : send_status(472, "<char> :is unknown mode char to me")
                                      - 'i' : channel.set_invite_only(sign == '+')
                                      - 't' : channel.set_topic_restricted(sign == '+')
                                      - 'k' : apply_mode_key(...)
                                      - 'o' : apply_mode_operator(...)
                                      - 'l' : apply_mode_limit(...)
                                      - other : send_status(472, "<char> :is unknown mode char to me")
                                                    │
                                                    ▼
                                    applied_modes.empty() || !state_changed? ──Yes──► (No broadcast, return)
                                                    │ No
                                                    ▼
                                    Broadcast MODE change to all channel members
```

---

## 2. Detailed Code-Level Edge Cases & Vulnerabilities

### A. Input Parsing & Grammar Edge Cases (`ServerCommands.cpp`, `ServerHelper.cpp`, `ServerChannelOps.cpp`)

#### 1. Unregistered Client Rejection (`ServerCommands.cpp:303-304`)
- **Code Reference**:
  ```cpp
  else if (!client.get_register_status())
      send_status(client, "451", ":You have not registered");
  ```
- **RFC Standard (RFC 2812 §3.1.5)**: Some IRC clients automatically query user modes or channel modes during handshake.
- **Flaw**: Rejecting all `MODE` invocations prior to registration completion is compliant with RFC 2812 §3.1.5 (`ERR_NOTREGISTERED`), but clients querying before registration receive `451`.

#### 2. User Mode (`MODE <nick>`) Completely Ignored / Silently Dropped (`ServerChannelOps.cpp:354-355`)
- **Code Reference**:
  ```cpp
  const Wire &channel_name = arguments[0];
  if (channel_name.empty() || channel_name[0] != '#')
      return ;
  ```
- **Flaw**: In standard IRC, `MODE <nickname>` queries user modes (returning `221 RPL_UMODEIS` e.g. `+i`). If `arguments[0]` is a user's nickname (or not starting with `#`), `handle_mode` silently returns with 0 response.
- **Impact**: Popular clients (irssi, HexChat, WeeChat) that query their own modes on connect will hang waiting for `221 RPL_UMODEIS` or receive no acknowledgment.

#### 3. Channel Prefix `'&'` (Local Channels) Omission (`ServerChannelOps.cpp:354` vs `ServerCommands.cpp:190`)
- **Code Reference**:
  - `ServerCommands.cpp:190`: `if (chan.empty() || (chan[0] != '#' && chan[0] != '&'))` (allows joining `&channel`)
  - `ServerChannelOps.cpp:354`: `if (channel_name.empty() || channel_name[0] != '#') return ;`
- **Flaw**: A user can join an `&` local channel via `JOIN &local`, but calling `MODE &local` or `MODE &local +i` is silently dropped because `channel_name[0] != '#'`.
- **Impact**: Channels starting with `&` cannot query modes or modify any channel modes.

#### 4. Colon Prefixes in Parameters Not Stripped (`ServerHelper.cpp:39-42`)
- **Code Reference**:
  ```cpp
  Vector<Wire> Server::split_arguments(const Wire &line) {
      return line.strAfter(" ").splitBy(' ').filter(is_empty);
  }
  ```
- **Consequences for MODE**:
  - `MODE :#chan` -> `arguments[0]` is `":#chan"`. Since `arguments[0][0] == ':' != '#'`, it silently drops!
  - `MODE #chan :+i` -> `arguments[1]` is `":+i"`. In the mode string loop, `mode_string[0]` is `':'` which triggers `472 : :is unknown mode char to me`.
  - `MODE #chan +k :secret` -> `arguments[2]` is `":secret"`. The channel key is stored as `":secret"` (literal colon included). Users attempting to join with `JOIN #chan secret` will be rejected with `475 (+k)`!
  - `MODE #chan +o :Alice` -> `arguments[2]` is `":Alice"`. Nick lookup for `":Alice"` fails with `401 :Alice :No such nick/channel`.
  - `MODE #chan +l :10` -> `arguments[2]` is `":10"`. `is_positive_number(":10")` fails with `461 MODE :Not enough parameters`.

---

### B. Mode Parameter Parsing & Execution Flaws (`ServerChannelOps.cpp`)

#### 5. Parameter Pre-Check vs. Execution Desynchronization (`ServerChannelOps.cpp:210-224`, `378-383`)
- **Code Reference**:
  ```cpp
  static size_t count_required_mode_parameters(const Wire &mode_string) {
      char sign = 0;
      size_t count = 0;
      for (size_t i = 0; i < mode_string.size(); ++i) {
          char c = mode_string[i];
          if (Wire("+-").contains(c))
              sign = c;
          else if ((sign == '+' && Wire("klo").contains(c)) || (sign == '-' && c == 'o'))
              count++;
      }
      return count;
  }
  ```
- **Flaws & Edge Cases**:
  1. **Invalid Numeric Limit Consumes Next Valid Parameter**:
     - Suppose an operator issues: `MODE #chan +l+k invalid_limit my_secret_key`.
     - `count_required_mode_parameters` calculates 2 required parameters (`+l` and `+k`).
     - Total arguments provided: 4 (`#chan`, `+l+k`, `invalid_limit`, `my_secret_key`), so pre-check PASSES.
     - In the loop:
       1. `+l` is evaluated with `arguments[2]` (`invalid_limit`). `is_positive_number("invalid_limit")` returns `false`.
       2. `apply_mode_limit` sends `461 MODE :Not enough parameters` and increments `param_index` to 3.
       3. `+k` is evaluated with `arguments[3]` (`my_secret_key`). It succeeds, sets the key, and marks `state_changed = true`.
       4. Result: The client receives error `461`, but the channel key `my_secret_key` IS applied and broadcast to all members!
  2. **Duplicate Mode Flags in Deduplication**:
     - `append_mode_change` deduplicates flags per sign block:
       ```cpp
       size_t last_sign_pos = applied_modes.find_last_of("+-");
       if (applied_modes.find(mode, last_sign_pos) == string::npos)
           applied_modes.push_back(mode);
       ```
     - If operator executes `MODE #chan +oo Alice Bob`:
       - `count_required_mode_parameters` requires 2 parameters.
       - Parameter 1 (`Alice`) appends `'o'` to `applied_modes` -> `"+o"`, and `" Alice"` to `applied_params`.
       - Parameter 2 (`Bob`): `applied_modes.find('o', 0)` finds `'o'` from Alice! So `'o'` is NOT appended to `applied_modes`. But `applied_params` += `" Bob"`.
       - The broadcast output is: `MODE #chan +o Alice Bob`!
       - IRC clients receiving `MODE #chan +o Alice Bob` parse only 1 parameter for `+o` (`Alice`) and ignore `Bob`!

#### 6. Inaccurate Mode Broadcast on Mixed No-Op / State Change (`ServerChannelOps.cpp:405-438`)
- **Code Reference**:
  ```cpp
  if (mode == 'i') {
      state_changed = channel.set_invite_only(sign == '+') || state_changed;
      append_mode_change(applied_modes, sign, 'i');
  }
  ```
- **Flaw**: `append_mode_change` is called regardless of whether `channel.set_invite_only()` returned `true` or `false`.
- **Scenario**:
  - Channel `#chan` is already `+i`.
  - Operator runs: `MODE #chan +i+t`.
  - `set_invite_only(true)` returns `false` (no change).
  - `set_topic_restricted(true)` returns `true` (changed).
  - `state_changed` is `true`.
  - Server broadcasts: `MODE #chan +it` to the channel.
  - Every channel member's client thinks `+i` was just set, desynchronizing local client state.
- **Silent Drop on Complete No-Op**:
  - If operator runs `MODE #chan +i` when `+i` is already active, `state_changed` is `false`.
  - `if (applied_modes.empty() || !state_changed) return;` silently drops the command without sending any reply.

#### 7. Non-Member Viewing Channel Modes Blocked (`ServerChannelOps.cpp:358-360`)
- **Code Reference**:
  ```cpp
  Channel &channel = ensure_channel_exists(client, channel_name);
  if (!channel || !ensure_channel_member(client, channel))
      return ;
  ```
- **RFC Standard (RFC 2812 §3.2.3)**: Any registered client can query the modes of a channel with `MODE #channel` without being a member.
- **Flaw**: `ensure_channel_member` rejects non-members with `442 <chan> :You're not on that channel`.

#### 8. Plaintext Key Exposure in `324 RPL_CHANNELMODEIS` (`ServerChannelOps.cpp:236-248`)
- **Code Reference**:
  ```cpp
  if (channel.has_key()) {
      current_modes.push_back('k');
      current_params += " " + channel.get_key();
  }
  ```
- **RFC Standard**: Channel keys should only be visible to channel operators or masked for regular members (e.g. `+k <key>` for ops, or `+k` with `<key>` omitted / replaced with `<key>` only for ops). In this implementation, any regular channel member issuing `MODE #channel` sees the plain text channel key.

---

### C. Channel State & Command Interactions

#### 9. Disconnect Ghost Operator FD Reuse Vulnerability (`ServerLoop.cpp:62-72` vs `Channel.cpp:119-126`)
- **Code Reference**:
  - `ServerLoop.cpp:65-69`:
    ```cpp
    for (ChannelMap::iterator it = get_channels().begin(); it != get_channels().end(); ++it) {
        it->second.remove_member(client_fd);
        if (it->second.empty())
            empty_channels.push_back(it->first);
    }
    ```
  - `Channel.cpp:119-125`:
    ```cpp
    void Channel::remove_client_from_channel(int client_fd) {
        remove_invited(client_fd);
        remove_operator(client_fd);
        remove_member(client_fd);
        if (empty() && server)
            server->remove_channel(name);
    }
    ```
- **The Critical Bug**:
  - `disconnect_client` in `ServerLoop.cpp` calls `channel.remove_member(client_fd)`.
  - It DOES NOT call `remove_operator(client_fd)` or `remove_invited(client_fd)`!
  - If client on FD `X` was an operator in `#chan`, and other members remain in `#chan`:
    - FD `X` is removed from `member_fds`, but REMAINS in `operator_fds`!
    - When a new client connects and is assigned the same FD `X` by the kernel, upon joining `#chan` (`channel.add_member(X)`), `channel.is_operator(X)` immediately evaluates to `true`!
  - **Impact**: New connections inheriting a reused socket FD automatically gain operator privileges and can issue `MODE #chan +o`, `KICK`, `TOPIC`, etc.

#### 10. Channel Key Blind Overwrite (`Channel.cpp:194-201`)
- **Code Reference**:
  ```cpp
  bool Channel::set_key(const Wire &key) {
      if (key_enabled && channel_key == key)
          return (false);
      channel_key = key;
      key_enabled = true;
      return (true);
  }
  ```
- **RFC Standard (RFC 2812 §3.2.3)**: If a channel key is already set, an operator must first remove it (`MODE #chan -k [key]`) before setting a new key, or the server must return `467 ERR_KEYSET :Channel key already set`.
- **Flaw**: Calling `MODE #chan +k newkey` silently overwrites the previous key without warning or error.

#### 11. Solitary Operator Demotion (Channel Zombie / Lockout State)
- **Scenario**:
  - A channel has 1 operator and multiple regular members.
  - The operator executes: `MODE #chan -o my_nick`.
  - `apply_mode_operator` removes operator rights from `my_nick`.
  - The channel now has `operator_fds.empty() == true`.
- **Consequences**:
  - If the channel is `+i` (invite only), no new members can be invited (INVITE requires op).
  - If the channel is `+t` (topic restricted), no one can update the topic (TOPIC requires op).
  - No one can ever set modes or promote a new operator (MODE requires op).
  - The channel remains in an un-administrable zombie state until all members leave and the channel is destroyed.

#### 12. Case Sensitivity in Target Nickname for `+o` / `-o` (`ServerChannelOps.cpp:289` & `Server.cpp:123-131`)
- **Code Reference**:
  - `ServerChannelOps.cpp:289`: `Client &target = get_client(target_nick);`
  - `Server.cpp:123-131`: `match_nickname(c, nick) { return c.get_nickname() == nick; }`
- **Flaw**: In IRC RFCs, nicknames are case-insensitive. If `Alice` is on the channel and an operator runs `MODE #chan +o alice`, `get_client("alice")` fails, returning `401 alice :No such nick/channel`.

#### 13. Numeric Validation for User Limit `+l` (`ServerHelper.cpp:6-9`)
- **Code Reference**:
  ```cpp
  bool Server::is_positive_number(const Wire &value) {
      return (value.toInt() > 0 && value.toInt().toStr() == value);
  }
  ```
- **Edge Cases**:
  - `MODE #chan +l 0` -> Rejected with `461 MODE :Not enough parameters`.
  - `MODE #chan +l -5` -> Rejected with `461`.
  - `MODE #chan +l +10` -> `value.toInt().toStr()` is `"10" != "+10"`, rejected with `461`.
  - `MODE #chan +l 010` -> `value.toInt().toStr()` is `"10" != "010"`, rejected with `461`.
  - `MODE #chan +l 99999999999999999999` -> `toInt()` integer overflow causes `_ok = false`, rejected with `461`.
  - Limit set lower than existing occupancy (e.g. 5 members on channel, `MODE #chan +l 2`): limit is set to 2; existing members remain, but all new `JOIN`s are rejected with `471 (+l)`.

#### 14. Unknown Mode Flags Error Reporting (`ServerChannelOps.cpp:401, 429`)
- **Code Reference**:
  ```cpp
  send_status(client, "472", Wire(mode) + " :is unknown mode char to me");
  ```
- **Behavior**: Any unrecognized character (e.g. `MODE #chan +z` or `MODE #chan +s` or `MODE #chan +m`) triggers `472`.
- **Sign Absence**: If an operator sends `MODE #chan i` (without `+` or `-`), `sign == 0`, triggering `472 i :is unknown mode char to me`.

---

## 3. Comprehensive Edge Cases Summary Table

| Category | Input / Trigger | Expected / RFC Behavior | Current Code Behavior | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **Prefix Support** | `MODE &local +i` | Set mode on local channel `&local` | Silently dropped (checks `chan[0] != '#'`) | Medium |
| **Colon Prefix** | `MODE #chan +k :pass` | Set key to `"pass"` | Sets key to `":pass"` (literal colon) | High |
| **Colon Prefix** | `MODE #chan +o :nick` | Promote `nick` | Fails with `401 :nick :No such nick` | High |
| **User Modes** | `MODE nick` / `MODE nick +i` | Return `221 RPL_UMODEIS` | Silently dropped | Medium |
| **Non-Member Query** | Non-member runs `MODE #chan` | Return `324 RPL_CHANNELMODEIS` | `442 :You're not on that channel` | Low |
| **FD Reuse / Security** | Operator disconnects, new client reuses FD | Clear operator status on disconnect | Ghost operator persists in `operator_fds` | Critical |
| **Key Overwrite** | `MODE #chan +k key2` when key1 set | `467 ERR_KEYSET` | Silently overwrites existing key | Low |
| **Deduplication** | `MODE #chan +oo user1 user2` | Apply `+o` to both users | Broadcasts `+o user1 user2` (malformed) | High |
| **Mixed Mode No-Op** | `MODE #chan +i+t` (where `+i` already set) | Broadcast only changed modes | Broadcasts `+it` claiming `+i` changed | Medium |
| **Parameter Starve** | `MODE #chan +l+k invalid key` | Reject entire command or limit | Sets key, reports limit error, broadcasts | Medium |
| **Nick Case** | `MODE #chan +o lowercase_nick` | Promote client matching nick (case-insensitive) | `401 :No such nick/channel` | Medium |
| **Channel Lockout** | Sole operator does `MODE #chan -o self` | Warning or allow lockout | Allows lockout; channel permanently unmanaged | Low |
