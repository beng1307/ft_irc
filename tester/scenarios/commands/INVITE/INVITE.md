# Comprehensive INVITE Command Flow & Edge Case Analysis

This document provides an exhaustive, line-by-line breakdown of the `INVITE` command lifecycle in `ft_irc`. It details input grammar edge cases, state transitions, security vulnerabilities, command interactions, adversarial threat models, and reachable failure modes.

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

## 3. Vulnerabilities, Edge Cases & Adversarial Threat Vectors

### VULN-INV-01: Ghost Invite FD Reuse (Access Control Bypass)
- **Severity**: **HIGH (Security Vulnerability)**
- **Test Scenario**: [`59_INVITE_ghost_invite_fd_reuse.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/59_INVITE_ghost_invite_fd_reuse.spec)
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

---

### VULN-INV-02: Target Unregistered State Leakage & Pre-Registration Invite
- **Severity**: **MEDIUM**
- **Test Scenario**: [`58_INVITE_unregistered_target_rejection.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/58_INVITE_unregistered_target_rejection.spec) (❌ FAILS against unpatched server)
- **Code Reference**: `Server.cpp:123-136` vs `ServerChannelOps.cpp:136-154`
- **Root Cause**:
  `get_client(target_nick)` searches `clients` map solely by `c.get_nickname() == nick`. It does not verify `c.get_register_status()`.
- **Failure Scenario**:
  1. An unauthenticated user connects and sends `NICK Bob`, but never sends `PASS` or `USER`.
  2. Alice in `#chan` runs `INVITE Bob #chan`.
  3. `target.send(make_msg(...))` sends raw IRC traffic to the unauthenticated TCP connection before registration / `001 RPL_WELCOME`.
  4. The unauthenticated socket FD is placed in `invited_fds`.
- **RFC Standard (RFC 2812 §3.2.7)**: Target must be a registered user; otherwise `401 ERR_NOSUCHNICK` should be returned.

---

### VULN-INV-03: Case-Sensitivity Mismatch in Channels and Nicknames
- **Severity**: **MEDIUM**
- **Test Scenarios**:
  - [`60_INVITE_case_insensitive_channel.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/60_INVITE_case_insensitive_channel.spec) (❌ FAILS against unpatched server)
  - [`61_INVITE_case_insensitive_nick.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/61_INVITE_case_insensitive_nick.spec) (❌ FAILS against unpatched server)
- **Code Reference**: `Server.cpp:123-136, 165-173`
- **Root Cause**:
  IRC specifications (RFC 1459 / 2812 §1.3) mandate case-insensitive matching for nicknames and channel names (`[`, `]`, `\`, `~` equivalence).
  In `ft_irc`, `channels.fetch(name)` and `match_nickname` use exact `Wire::operator==` (case-sensitive string comparison).

---

### VULN-INV-04: Mandatory Operator Requirement on Public (`-i`) Channels
- **Severity**: **LOW / RFC Non-Compliance**
- **Test Scenario**: [`55_INVITE_non_op_on_regular_channel.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/55_INVITE_non_op_on_regular_channel.spec) (❌ FAILS against unpatched server)
- **Code Reference**: `ServerChannelOps.cpp:132-134`
- **Root Cause**:
  `handle_invite` unconditionally executes `if (!ensure_channel_operator(client, channel)) return ;`.
- **RFC Standard (RFC 2812 §3.2.7)**:
  On regular, non-invite-only channels (`-i`), **any channel member** is permitted to invite users.

---

### VULN-INV-05: Adversarial Nick Takeover / Impersonation Attack
- **Severity**: **HIGH (Security Architecture Verification)**
- **Test Scenario**: [`76_INVITE_nick_takeover_attacker_blocked.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/76_INVITE_nick_takeover_attacker_blocked.spec) (✅ Verified Protected)
- **Attack Scenario**:
  1. Op invites `Bob` (socket FD 10) to `+i #secret`.
  2. Bob changes his nickname to `Bobby`.
  3. Attacker Mallory connects, sends `NICK Bob` (socket FD 11) claiming the vacated nickname.
  4. Mallory sends `JOIN #secret` attempting to hijack Bob's pending invitation.
- **Protection**: Invitations are bound to the client socket session, not the reclaimed nickname string. Mallory is rejected with `473 ERR_INVITEONLYCHAN`.

---

### VULN-INV-06: Channel Existence Oracle Information Leakage
- **Severity**: **LOW / Privacy Leakage**
- **Test Scenario**: [`77_INVITE_channel_existence_oracle_leak.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/77_INVITE_channel_existence_oracle_leak.spec) (✅ Verified)
- **Vulnerability**:
  An external attacker probes channel names by sending `INVITE Alice <target_channel>`.
  - If `<target_channel>` does not exist -> server returns `403 ERR_NOSUCHCHANNEL`.
  - If `<target_channel>` exists -> server returns `442 ERR_NOTONCHANNEL`.
  - This allows an unprivileged client to map out all private channel names on the server without joining them.

---

## 4. Cross-Command Interaction Matrix

| Command Interaction | State / Flow Impact | Edge Case / Risk | Verified Test Scenario |
|---|---|---|---|
| **INVITE + JOIN** | `JOIN` checks `channel.is_invited(fd)`. If valid, removes FD from `invited_fds` and adds to `member_fds`. | **Single-use enforcement**: Invite is consumed on join. If member leaves (`PART`/`KICK`), they cannot rejoin without a new invite. | [`64_INVITE_single_use_consumption.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/64_INVITE_single_use_consumption.spec) |
| **INVITE + JOIN (+l)** | Channel at capacity (`+l`) rejects invited user with `471`. Invite is preserved in `invited_fds`. | **Capacity enforcement**: Invite does not override channel user limits. Client can join once a member leaves. | [`72_INVITE_limit_saturation_blocks_invited_user.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/72_INVITE_limit_saturation_blocks_invited_user.spec) |
| **INVITE + JOIN (+k)** | Channel with key (`+k`) rejects invited user without key (`475`). Invite is preserved. | **Key enforcement**: Invite does not bypass channel passwords. Client can retry with key. | [`73_INVITE_key_enforcement_not_bypassed.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/73_INVITE_key_enforcement_not_bypassed.spec) |
| **INVITE + Multi-Channel** | Target invited to `#chanA` and `#chanB`. Joins `#chanA` then `#chanB`. | **Isolation**: Consuming invite on `#chanA` has zero effect on `#chanB`. | [`74_INVITE_multi_channel_independent_invites.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/74_INVITE_multi_channel_independent_invites.spec) |
| **INVITE + Op Demotion/Kick** | Op invites user, then issuing op is de-opped (`-o`) or kicked. | **State preservation**: Target can still join because invitation is recorded in channel state. | [`75_INVITE_op_demotion_or_kick_preserves_invite.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/75_INVITE_op_demotion_or_kick_preserves_invite.spec) |
| **INVITE + Nick Takeover** | Attacker claims previous nickname of an invited user. | **Session pinning**: Attacker is blocked (`473`); original user joins under new nick. | [`76_INVITE_nick_takeover_attacker_blocked.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/76_INVITE_nick_takeover_attacker_blocked.spec) |
| **INVITE + KICK + Mode Reset** | Invited user joins, is kicked, `+i` is toggled off and on. | **Wipe guarantee**: Kicking purges all invites. Kicked user cannot rejoin when `+i` returns. | [`79_INVITE_kick_purges_all_pending_and_active_invite.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/79_INVITE_kick_purges_all_pending_and_active_invite.spec) |

---

## 5. Complete Test Scenario Inventory

The following 29 `.spec` test scenarios in [`tester/scenarios/commands/INVITE/`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE) provide total coverage across normal, adversarial, and edge-case behaviors:

| # | Spec File Name | Description & Tested Edge Case | Result on Unpatched Server |
|---|---|---|---|
| 51 | [`51_INVITE_not_registered.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/51_INVITE_not_registered.spec) | Unregistered sender receives `451 ERR_NOTREGISTERED` | ✅ PASS |
| 52 | [`52_INVITE_missing_params.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/52_INVITE_missing_params.spec) | Missing arguments (`< 2`) triggers `461 ERR_NEEDMOREPARAMS` | ✅ PASS |
| 53 | [`53_INVITE_nonexistent_channel.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/53_INVITE_nonexistent_channel.spec) | Inviting to non-existent channel returns `403 ERR_NOSUCHCHANNEL` | ✅ PASS |
| 54 | [`54_INVITE_not_on_channel.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/54_INVITE_not_on_channel.spec) | Non-member sender receives `442 ERR_NOTONCHANNEL` | ✅ PASS |
| 55 | [`55_INVITE_non_op_on_regular_channel.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/55_INVITE_non_op_on_regular_channel.spec) | Non-op inviting on public (`-i`) channel (RFC allows; server blocks `482`) | ❌ FAIL (Bug detected) |
| 56 | [`56_INVITE_nonexistent_target_nick.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/56_INVITE_nonexistent_target_nick.spec) | Non-existent target nick returns `401 ERR_NOSUCHNICK` | ✅ PASS |
| 57 | [`57_INVITE_target_already_on_channel.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/57_INVITE_target_already_on_channel.spec) | Target already in channel returns `443 ERR_USERONCHANNEL` | ✅ PASS |
| 58 | [`58_INVITE_unregistered_target_rejection.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/58_INVITE_unregistered_target_rejection.spec) | Inviting unauthenticated target leaks traffic instead of `401` | ❌ FAIL (Bug detected) |
| 59 | [`59_INVITE_ghost_invite_fd_reuse.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/59_INVITE_ghost_invite_fd_reuse.spec) | Recycled FD inherits stale pending invite to `+i` channel | ✅ PASS |
| 60 | [`60_INVITE_case_insensitive_channel.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/60_INVITE_case_insensitive_channel.spec) | Case-insensitive channel name matching (`#secretchan` vs `#SecretChan`) | ❌ FAIL (Bug detected) |
| 61 | [`61_INVITE_case_insensitive_nick.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/61_INVITE_case_insensitive_nick.spec) | Case-insensitive target nick matching (`bob` vs `Bob`) | ❌ FAIL (Bug detected) |
| 62 | [`62_INVITE_colon_prefix_channel.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/62_INVITE_colon_prefix_channel.spec) | Colon-prefixed channel parameter (`INVITE Bob :#secret`) | ✅ PASS |
| 63 | [`63_INVITE_colon_prefix_target_nick.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/63_INVITE_colon_prefix_target_nick.spec) | Colon-prefixed target nick parameter (`INVITE :Bob #secret`) | ❌ FAIL (Bug detected) |
| 64 | [`64_INVITE_single_use_consumption.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/64_INVITE_single_use_consumption.spec) | Invitation is single-use: consumed on `JOIN`, re-joining fails `473` | ✅ PASS |
| 65 | [`65_INVITE_key_and_limit_retry_preservation.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/65_INVITE_key_and_limit_retry_preservation.spec) | Failed join (+k / +l) preserves invite for retry | ✅ PASS |
| 66 | [`66_INVITE_nick_change_preservation.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/66_INVITE_nick_change_preservation.spec) | Target changes nick (`NICK NewName`) before joining | ✅ PASS |
| 67 | [`67_INVITE_relay_message_format.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/67_INVITE_relay_message_format.spec) | Verifies `341 RPL_INVITING` and relay notice formatting | ✅ PASS |
| 68 | [`68_INVITE_self_invite_rejected.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/68_INVITE_self_invite_rejected.spec) | Self-invite by operator rejected with `443 ERR_USERONCHANNEL` | ✅ PASS |
| 69 | [`69_INVITE_trailing_tokens_ignored.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/69_INVITE_trailing_tokens_ignored.spec) | Extra trailing tokens ignored without error | ✅ PASS |
| 70 | [`70_INVITE_mode_toggle_persistence.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/70_INVITE_mode_toggle_persistence.spec) | Invitations persist across channel mode toggles (`+i -> -i -> +i`) | ✅ PASS |
| 71 | [`71_INVITE_empty_channel_recreated_clean.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/71_INVITE_empty_channel_recreated_clean.spec) | Emptied/destroyed channel clears pending invitations | ✅ PASS |
| 72 | [`72_INVITE_limit_saturation_blocks_invited_user.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/72_INVITE_limit_saturation_blocks_invited_user.spec) | Channel capacity limit (`+l`) blocks invited user with `471` | ✅ PASS |
| 73 | [`73_INVITE_key_enforcement_not_bypassed.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/73_INVITE_key_enforcement_not_bypassed.spec) | Channel password key (`+k`) is not bypassed by invitation (`475`) | ✅ PASS |
| 74 | [`74_INVITE_multi_channel_independent_invites.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/74_INVITE_multi_channel_independent_invites.spec) | Independent multi-channel invitation tracking and isolation | ✅ PASS |
| 75 | [`75_INVITE_op_demotion_or_kick_preserves_invite.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/75_INVITE_op_demotion_or_kick_preserves_invite.spec) | Issuing operator demotion or kick does not invalidate pending invite | ✅ PASS |
| 76 | [`76_INVITE_nick_takeover_attacker_blocked.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/76_INVITE_nick_takeover_attacker_blocked.spec) | Attacker claiming invited user's old nickname is blocked (`473`) | ✅ PASS |
| 77 | [`77_INVITE_channel_existence_oracle_leak.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/77_INVITE_channel_existence_oracle_leak.spec) | External channel existence enumeration probe (`403` vs `442`) | ✅ PASS |
| 78 | [`78_INVITE_comma_separated_channel_rejection.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/78_INVITE_comma_separated_channel_rejection.spec) | Comma-separated channel list injection rejected with `403` | ✅ PASS |
| 79 | [`79_INVITE_kick_purges_all_pending_and_active_invite.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/INVITE/79_INVITE_kick_purges_all_pending_and_active_invite.spec) | Kicking purges all invites; cannot rejoin when `+i` returns | ✅ PASS |
