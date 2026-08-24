# Comprehensive INVITE Command Flow & Edge Case Analysis

This document provides an exhaustive, line-by-line breakdown of the `INVITE` command lifecycle in `ft_irc`. It details input grammar edge cases, state transitions, security vulnerabilities, command interactions, and reachable failure modes.

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
!client.get_register_status()                command == "INVITE"
        │                                           │
        ▼                                           ▼
send_status(451,                            Server::handle_invite
":You have not registered")                         │
                                                    ▼
                                    arguments.size() < 2? ──Yes──► send_status(461, "INVITE :Not enough parameters")
                                                    │ No
                                                    ▼
                                    target_nick = arguments[0]
                                    channel_name = arguments[1]
                                                    │
                                                    ▼
                                    ensure_channel_exists(client, channel_name)
                                    !channel? ──Yes──► send_status(403, "<chan> :No such channel")
                                                    │ No
                                                    ▼
                                    ensure_channel_member(client, channel)
                                    !channel.has_member(client)? ──Yes──► send_status(442, "<chan> :You're not on that channel")
                                                    │ No
                                                    ▼
                                    ensure_channel_operator(client, channel)
                                    !channel.is_operator(client)? ──Yes──► send_status(482, "<chan> :You're not channel operator")
                                                    │ No
                                                    ▼
                                    target = get_client(target_nick)
                                    !target? ──Yes──► send_status(401, "<target> :No such nick/channel")
                                                    │ No
                                                    ▼
                                    channel.has_member(target.get_socket())?
                                                    │ Yes ──► send_status(443, "<target> <chan> :is already on channel")
                                                    │ No
                                                    ▼
                                    target.send(make_msg(client, "INVITE", target_nick, channel_name))
                                    send_status(client, "341", target_nick + " " + channel_name)
                                    channel.add_invited(target.get_socket())
```

---

## 2. Code Walkthrough & State Machine

### Execution Flow in `ServerChannelOps.cpp` (`handle_invite`)
```cpp
void	Server::handle_invite(Client &client, const Vector<Wire> &arguments)
{
    // Step 1: Parameter Count Check
    if (arguments.size() < 2)
    {
        send_status(client, "461", "INVITE :Not enough parameters");
        return ;
    }

    // Step 2: Extract Parameters
    const Wire &target_nick = arguments[0];
    const Wire &channel_name = arguments[1];

    // Step 3: Channel Existence Validation
    Channel &channel = ensure_channel_exists(client, channel_name);
    if (!channel)
        return ;

    // Step 4: Sender Membership Validation
    if (!ensure_channel_member(client, channel))
        return ;

    // Step 5: Operator Rights Validation (Unconditional in ft_irc)
    if (!ensure_channel_operator(client, channel))
        return ;

    // Step 6: Target Client Lookup
    Client &target = get_client(target_nick);
    if (!target)
    {
        send_status(client, "401", target_nick + " :No such nick/channel");
        return ;
    }

    // Step 7: Target Already on Channel Check
    if (channel.has_member(target.get_socket()))
    {
        send_status(client, "443", Wire(target_nick, " ", channel_name, " :is already on channel"));
        return ;
    }

    // Step 8: Send Notification to Target and Confirmation to Inviter
    target.send(make_msg(client, "INVITE", target_nick, channel_name));
    send_status(client, "341", target_nick + " " + channel_name);

    // Step 9: Register Invitation in Channel State
    channel.add_invited(target.get_socket());
}
```

---

## 3. Vulnerabilities, Edge Cases & Attack Surface

### VULN-INV-01: Ghost Invite FD Reuse (Access Control Bypass)
- **Severity**: **HIGH (Security Vulnerability)**
- **Code Reference**: `ServerLoop.cpp:62-72` vs `Channel.cpp:158-166`
- **Root Cause**:
  When a client disconnects, `Server::disconnect_client(int client_fd)` calls:
  ```cpp
  for (ChannelMap::iterator it = get_channels().begin(); it != get_channels().end(); ++it) {
      it->second.remove_member(client_fd);
      if (it->second.empty())
          empty_channels.push_back(it->first);
  }
  ```
  `disconnect_client` only calls `remove_member(client_fd)`. It **never** calls `remove_invited(client_fd)`.
- **Attack / Failure Scenario**:
  1. Alice (op) creates private invite-only channel `+i #secret`.
  2. Alice invites Bob (`socket_fd = 5`) via `INVITE Bob #secret`.
  3. Bob's FD `5` is inserted into `#secret`'s `invited_fds` set.
  4. Bob disconnects without ever joining `#secret`.
  5. `#secret` still contains FD `5` in its `invited_fds` set.
  6. Charlie connects to the IRC server. The OS kernel recycles FD `5` and assigns it to Charlie.
  7. Charlie authenticates and sends `JOIN #secret`.
  8. `Server::let_client_join_channel` checks `channel.is_invited(client_fd)`. Since `client_fd == 5`, this returns `true`!
  9. Charlie joins `#secret` without ever being invited by Alice.
- **Remediation**: In `Server::disconnect_client`, iterate all channels and call `channel.remove_invited(client_fd)` (or use `remove_client_from_channel(client_fd)`).

---

### VULN-INV-02: Target Unregistered State Leakage
- **Severity**: **MEDIUM**
- **Code Reference**: `Server.cpp:123-136` vs `ServerChannelOps.cpp:136-154`
- **Root Cause**:
  `get_client(target_nick)` searches `clients` map solely by `c.get_nickname() == nick`. It does not check `c.get_register_status()`.
- **Failure Scenario**:
  1. An unauthenticated attacker connects and sends `NICK Bob`, but never sends `PASS` or `USER`.
  2. Alice in `#chan` runs `INVITE Bob #chan`.
  3. `target.send(make_msg(...))` sends raw IRC traffic to the unauthenticated TCP connection before registration / `RPL_WELCOME (001)`.
  4. The unauthenticated socket FD is placed in `invited_fds`.
- **RFC Standard (RFC 2812 §3.2.7)**: Target must be a registered user; otherwise `401 ERR_NOSUCHNICK` should be returned.

---

### VULN-INV-03: Case-Sensitivity Mismatch in Channels and Nicknames
- **Severity**: **MEDIUM**
- **Code Reference**: `Server.cpp:123-136, 165-173`
- **Root Cause**:
  IRC specifications (RFC 1459 / 2812 §1.3) mandate case-insensitive matching for nicknames and channel names (`[`, `]`, `\`, `~` equivalence).
  In `ft_irc`, `channels.fetch(name)` and `match_nickname` use exact `Wire::operator==` (case-sensitive `std::string` comparison).
- **Failure Scenario**:
  1. Channel `#InviteCase` exists with `+i`.
  2. Op runs `INVITE Alice #invitecase`.
  3. `ensure_channel_exists` looks for `#invitecase` in `channels` map, fails to find `#InviteCase`, and aborts with `403 ERR_NOSUCHCHANNEL`.
  4. Similarly, if Alice is registered as `Alice`, `INVITE alice #InviteCase` fails with `401 ERR_NOSUCHNICK`.

---

### VULN-INV-04: Mandatory Operator Requirement on Public (`-i`) Channels
- **Severity**: **LOW / RFC Non-Compliance**
- **Code Reference**: `ServerChannelOps.cpp:132-134`
- **Root Cause**:
  `handle_invite` unconditionally executes `if (!ensure_channel_operator(client, channel)) return ;`.
- **RFC Standard (RFC 2812 §3.2.7)**:
  "When the channel has invite-only flag set (+i), only channel operators may issue invitations."
  On regular, non-invite-only channels (`-i`), **any channel member** is permitted to invite users.
- **Behavior in `ft_irc`**: Regular members attempting `INVITE` on a public channel are always blocked with `482 ERR_CHANOPRIVSNEEDED`.

---

### VULN-INV-05: Rejection of Invites to Non-Existent Channels
- **Severity**: **LOW / RFC Non-Compliance**
- **Code Reference**: `ServerChannelOps.cpp:127-129`
- **Root Cause**:
  `handle_invite` calls `ensure_channel_exists`, which sends `403 ERR_NOSUCHCHANNEL` if the channel is not active.
- **RFC Standard (RFC 2812 §3.2.7)**:
  "There is no requirement that the channel the target user is being invited to must exist or be a valid channel."
- **Behavior in `ft_irc`**: Users cannot use `INVITE` to suggest or designate a new channel room before creating it.

---

### VULN-INV-06: Colon-Prefixed Parameter Parsing Glitch
- **Severity**: **MEDIUM**
- **Code Reference**: `ServerHelper.cpp:39-42` (`split_arguments`)
- **Root Cause**:
  Standard IRC clients frequently format commands with a trailing colon for the final argument:
  `INVITE Bob :#secret`
  `split_arguments` tokenizes by spaces and leaves the leading colon on the argument string.
- **Failure Scenario**:
  1. Client sends `INVITE Bob :#secret`.
  2. `arguments[0]` is `"Bob"`, `arguments[1]` is `":#secret"`.
  3. `ensure_channel_exists` searches for channel named literally `":#secret"`.
  4. Lookup fails, returning `403 :#secret :No such channel`.
  5. If client sends `INVITE :Bob #secret`, `arguments[0]` is `":Bob"`, returning `401 :Bob :No such nick/channel`.

---

### VULN-INV-07: SendQ Saturation via Unbounded Invite Flooding
- **Severity**: **MEDIUM (Denial of Service / Harassment)**
- **Code Reference**: `ServerChannelOps.cpp:150-154`
- **Root Cause**:
  `handle_invite` does not rate-limit or prevent duplicate invitations to the same target before the target joins.
- **Failure Scenario**:
  1. Op spams `INVITE Victim #chan` thousands of times.
  2. Target client's `out_buffer` fills up with `INVITE` notices.
  3. Target hits `MAX_OUTPUT_BUFFER_SIZE` (1MB) in `ServerLoop.cpp:117` and is forcibly disconnected by the server (`SendQ exceeded`).

---

### VULN-INV-08: Stale Invite Persistence Across Mode Changes
- **Severity**: **LOW**
- **Code Reference**: `Channel.cpp:168-174`
- **Root Cause**:
  Toggling channel mode from `+i` to `-i` and back to `+i` (`set_invite_only`) does not clear `invited_fds`.
- **Behavior**:
  An invitation issued hours earlier while `+i` was enabled remains valid indefinitely if `+i` is toggled off and on again, unless the target joins or the channel is completely destroyed.

---

### VULN-INV-09: Inability to Revoke Pending Invitations
- **Severity**: **LOW**
- **Code Reference**: `ServerChannelOps.cpp:92-96` (`handle_kick`)
- **Root Cause**:
  `handle_kick` requires the target to already be a member (`channel.has_member(target.get_socket())`).
- **Behavior**:
  If an operator accidentally invites an unwanted user to `+i #secret`, the operator cannot cancel or revoke the invite via `KICK` before the user joins. The operator's only remedy is destroying the channel or changing channel modes/keys.

---

## 4. Cross-Command Interaction Matrix

| Command Interaction | State / Flow Impact | Edge Case / Risk |
|---|---|---|
| **INVITE + JOIN** | `JOIN` checks `channel.is_invited(fd)`. If valid, removes FD from `invited_fds` and adds to `member_fds`. | **Single-use enforcement**: Invite is consumed on join. If member leaves (`PART`/`KICK`), they cannot rejoin without a new invite. |
| **INVITE + JOIN (+k / +l)** | If channel has `+i` AND `+k` or `+l`, invite satisfies `+i`. If `+k` or `+l` fails, `remove_invited` is **not** called. | **Invite preservation**: Client can retry `JOIN` with key or after limit clears without needing a new invite. |
| **INVITE + NICK** | Target is invited, then executes `NICK NewName` before joining. | **FD Tracking**: Because invitations are tracked by socket FD, `JOIN` succeeds under the new nickname. |
| **INVITE + QUIT / DISCONNECT** | Target is invited, then disconnects before joining. | **VULN-INV-01 Ghost Invite**: FD remains in `invited_fds`. Recycled FD allows new client unauthorized entry. |
| **INVITE + KICK** | Op tries to kick a pending invited user before they join. | Returns `441 ERR_USERNOTINCHANNEL`. Pending invite cannot be revoked via `KICK`. |
| **INVITE + PART (Channel Emptied)** | All channel members leave (`PART`), destroying the channel object. | New channel created with same name starts with fresh, empty `invited_fds`. |
| **INVITE + MODE (+i / -i)** | Op toggles `+i` off and back on. | Pending invites in `invited_fds` remain active across mode toggles. |
| **INVITE + PRIVMSG** | Inviter can send invite notifications even if target has not opened a direct query. | Potential spam vector if invite flooding is unthrottled. |

---

## 5. Numeric Replies & Error Code Precedence

The following table lists all status codes generated during the `INVITE` execution lifecycle in evaluation order:

| Step | Numeric Code | Name | Trigger Condition in `ft_irc` |
|---|---|---|---|
| 1 | `451` | `ERR_NOTREGISTERED` | Sender is not registered (`!client.get_register_status()`). |
| 2 | `461` | `ERR_NEEDMOREPARAMS` | Command parameters count `< 2` (`INVITE :Not enough parameters`). |
| 3 | `403` | `ERR_NOSUCHCHANNEL` | Target channel does not exist in `channels` map. |
| 4 | `442` | `ERR_NOTONCHANNEL` | Sender is not a member of the target channel. |
| 5 | `482` | `ERR_CHANOPRIVSNEEDED` | Sender is not an operator on the target channel. |
| 6 | `401` | `ERR_NOSUCHNICK` | Target nickname does not exist in `clients` map. |
| 7 | `443` | `ERR_USERONCHANNEL` | Target user is already a member of the channel. |
| 8 | `341` | `RPL_INVITING` | **Success**: Confirmation sent to inviter (`341 <target_nick> <chan>`). |
| - | (Relay) | `INVITE` | **Success**: Relay message sent to target (`:<inviter> INVITE <target> :<chan>`). |
