# Test Coverage Audit: Tested vs. Missing Behaviors

## 1. Executive Summary

This document cross-references all 67 itemized behaviors from [expected_behavior.md](file:///home/tbatis/core/berg/tester/TestcaseIdeation/expected_behavior.md) against the active test scenarios in [`/home/tbatis/core/berg/tester/scenarios/`](file:///home/tbatis/core/berg/tester/scenarios).

### Summary Statistics
- **Total Expected Behaviors**: 67
- **Fully Covered / Tested**: 67 (100.0%)
- **Partially Covered**: 0 (0.0%)
- **Completely Missing**: 0 (0.0%)

---

## 2. Detailed Audit by Category

#### Category 1: Network, Framing & Multiplexing Core (NET)

| ID | Behavior Description | Status | Current Test Scenario | Gap / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **NET-01** | CRLF line endings | **COVERED** | All standard `.spec` files (`SEND`) | None. |
| **NET-02** | Bare `\n` (LF) line endings | **COVERED** | `27_framing_and_delimiters.spec` | Verified via `SEND_RAW USER alice 0 * :Alice LF\n`. |
| **NET-03** | TCP Packet Fragmentation | **COVERED** | `02_fragmentation.spec`, `13_command_case_and_fragmentation.spec` | Verified across split chunks. |
| **NET-04** | Concatenated / Pipelined frames | **COVERED** | `13_command_case_and_fragmentation.spec` | Multiple commands in single raw packet. |
| **NET-05** | Empty lines & extra whitespace | **COVERED** | `27_framing_and_delimiters.spec` | Verified via `SEND_RAW \r\n\r\n PASS 1234 \r\n`. |
| **NET-06** | 512-byte line buffer limit | **COVERED** | `27_framing_and_delimiters.spec` | Verified buffer safety on 550-byte raw payload. |
| **NET-07** | Concurrent client multiplexing | **COVERED** | `28_high_concurrency_multiplexing.spec` | 10 simultaneous active clients on shared channel. |
| **NET-08** | Abrupt disconnect (FIN/RST) | **COVERED** | `22_abrupt_close_and_reconnect.spec` | Uses `RESET` / `EXPECT_DISCONNECT`. |
| **NET-09** | Disconnect mid-fragment | **COVERED** | `27_framing_and_delimiters.spec` | Partial `NICK PartialNic` + `RESET` + reconnect recovery. |
| **NET-10** | Paused client (`SIGSTOP` & flood) | **COVERED** | `23_pause_and_bounded_flood.spec` | Uses `PAUSE`, `FLOOD 10`, `RESUME`. |

---

### Category 2: Connection Registration & Authentication (AUTH)

| ID | Behavior Description | Status | Current Test Scenario | Gap / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-01** | Standard `PASS` $\to$ `NICK` $\to$ `USER` | **COVERED** | Tested across almost all specs | Verified `001..004` replies. |
| **AUTH-02** | Permuted `PASS` $\to$ `USER` $\to$ `NICK` | **COVERED** | `25_registration_gating_and_modes.spec` | Verified `PASS` $\to$ `USER` $\to$ `NICK` sequence. |
| **AUTH-03** | Incorrect password rejection | **COVERED** | `01_pass_failure.spec` | Verified `464 ERR_PASSWDMISMATCH`. |
| **AUTH-04** | Duplicate `PASS` post-registration | **COVERED** | `25_registration_gating_and_modes.spec` | Verified `462 ERR_ALREADYREGISTRED`. |
| **AUTH-05** | Pre-registration command gating | **COVERED** | `25_registration_gating_and_modes.spec` | Verified `JOIN`, `PRIVMSG`, `MODE`, `TOPIC` return `451 ERR_NOTREGISTERED`. |
| **AUTH-06** | `NICK` parameter missing | **COVERED** | `11_parameter_errors.spec` | Verified `431 ERR_NONICKNAMEGIVEN`. |
| **AUTH-07** | `NICK` erroneous characters | **COVERED** | `26_dynamic_nick_change_and_errors.spec` | Verified `432 ERR_ERRONEUSNICKNAME` for `123digit`, `#bad`. |
| **AUTH-08** | `NICK` collision during registration | **COVERED** | `12_duplicate_nick_recovery.spec` | Verified `433 ERR_NICKNAMEINUSE` and recovery. |
| **AUTH-09** | Dynamic `NICK` change post-reg | **COVERED** | `26_dynamic_nick_change_and_errors.spec` | Verified `:old NICK :new` broadcast to peers. |
| **AUTH-10** | Dynamic `NICK` change collision | **COVERED** | `26_dynamic_nick_change_and_errors.spec` | Verified `433 ERR_NICKNAMEINUSE` keeps original nick. |
| **AUTH-11** | `USER` parameter count validation | **COVERED** | `11_parameter_errors.spec` | Verified `461 ERR_NEEDMOREPARAMS`. |
| **AUTH-12** | Duplicate `USER` post-registration | **COVERED** | `25_registration_gating_and_modes.spec` | Verified `462 ERR_ALREADYREGISTRED`. |
| **AUTH-13** | `CAP LS` / `CAP END` negotiation | **COVERED** | `25_registration_gating_and_modes.spec` | Verified client handshake with `CAP LS` / `CAP END`. |

---

### Category 3: Keepalive & Connection Lifecycle (LIFE)

| ID | Behavior Description | Status | Current Test Scenario | Gap / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **LIFE-01** | `PING <token>` $\to$ `PONG` reply | **COVERED** | `24_ping_pong_and_quit.spec` | Verified `PING 12345` $\to$ `PONG * :12345`. |
| **LIFE-02** | `PING :<token>` trailing syntax | **COVERED** | `24_ping_pong_and_quit.spec` | Verified `PING :heartbeat` $\to$ `PONG * :heartbeat`. |
| **LIFE-03** | `PING` with empty/missing token | **COVERED** | `24_ping_pong_and_quit.spec` | Verified server handles empty `PING` gracefully. |
| **LIFE-04** | `QUIT` with custom reason | **COVERED** | `10_client_disconnect.spec` | Verified broadcast `:Alice!* QUIT :Leaving server`. |
| **LIFE-05** | `QUIT` without parameter | **COVERED** | `24_ping_pong_and_quit.spec` | Verified bare `QUIT` broadcast & clean disconnect. |
| **LIFE-06** | `QUIT` frees nick & resources | **COVERED** | `10_client_disconnect.spec`, `22_abrupt_close_and_reconnect.spec`, `24_ping_pong_and_quit.spec` | Reconnecting with same nick succeeds. |
| **LIFE-07** | `QUIT` before registration | **COVERED** | `24_ping_pong_and_quit.spec` | Unregistered client `QUIT` closes socket cleanly. |

---

### Category 4: Channel Membership & Navigation (CHAN)

| ID | Behavior Description | Status | Current Test Scenario | Gap / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **CHAN-01** | `JOIN` creates channel & grants op | **COVERED** | `04_channel_join_and_broadcast.spec`, `05_invite_and_kick.spec` | Verified `@` in names & initial operator privilege. |
| **CHAN-02** | `JOIN` existing channel as member | **COVERED** | `04_channel_join_and_broadcast.spec` | Verified member join broadcast. |
| **CHAN-03** | `JOIN` self-broadcast | **COVERED** | `04_channel_join_and_broadcast.spec` | Verified joiner receives own `JOIN`. |
| **CHAN-04** | `JOIN` invalid channel name | **COVERED** | `29_membership_and_param_errors.spec` | Verified `JOIN invalidchannel` returns `403 ERR_NOSUCHCHANNEL`. |
| **CHAN-05** | `JOIN` missing parameter | **COVERED** | `29_membership_and_param_errors.spec` | Verified `JOIN` with no args returns `461 ERR_NEEDMOREPARAMS`. |
| **CHAN-06** | `JOIN` already joined channel | **COVERED** | `29_membership_and_param_errors.spec` | Verified re-joining active channel handles cleanly. |
| **CHAN-07** | `PART` with reason | **COVERED** | `16_part_and_rejoin.spec` | Verified `:Bob!* PART #part :Leaving now`. |
| **CHAN-08** | `PART` without reason | **COVERED** | `29_membership_and_param_errors.spec` | Verified bare `PART #channel` broadcast. |
| **CHAN-09** | `PART` destruction on last member | **COVERED** | `29_membership_and_param_errors.spec` | Verified re-creation after last member parts grants operator. |
| **CHAN-10** | `PART` user not on channel | **COVERED** | `29_membership_and_param_errors.spec` | Verified `PART #notjoined` returns `442 ERR_NOTONCHANNEL`. |
| **CHAN-11** | `PART` nonexistent channel | **COVERED** | `29_membership_and_param_errors.spec` | Verified `PART #nonexistent` returns `403 ERR_NOSUCHCHANNEL`. |
| **CHAN-12** | `PART` missing parameter | **COVERED** | `29_membership_and_param_errors.spec` | Verified bare `PART` returns `461 ERR_NEEDMOREPARAMS`. |

---

### Category 5: Messaging & Communication (MSG)

| ID | Behavior Description | Status | Current Test Scenario | Gap / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **MSG-01** | `PRIVMSG #chan` broadcast | **COVERED** | `04_channel_join_and_broadcast.spec`, `15_recipient_isolation.spec` | Relayed to members. |
| **MSG-02** | Sender isolation (no echo) | **COVERED** | `15_recipient_isolation.spec` | Verified sender does not receive own message. |
| **MSG-03** | Direct private message | **COVERED** | `03_basic_registration_and_privmsg.spec`, `15_recipient_isolation.spec` | Delivered strictly to recipient. |
| **MSG-04** | `PRIVMSG` missing recipient | **COVERED** | `14_negative_targets.spec` | Verified `411 ERR_NORECIPIENT`. |
| **MSG-05** | `PRIVMSG` missing text | **COVERED** | `30_msg_edge_cases_and_formatting.spec` | Verified `PRIVMSG Bob` (no text) returns `412 ERR_NOTEXTTOSEND`. |
| **MSG-06** | `PRIVMSG` nonexistent nick | **COVERED** | `14_negative_targets.spec` | Verified `401 ERR_NOSUCHNICK`. |
| **MSG-07** | `PRIVMSG` nonexistent channel | **COVERED** | `14_negative_targets.spec` | Verified `403 ERR_NOSUCHCHANNEL`. |
| **MSG-08** | Colons/spaces preservation | **COVERED** | `30_msg_edge_cases_and_formatting.spec` | Verified trailing parameters with multiple colons and spacing. |

---

### Category 6: Topic Management (TOPIC)

| ID | Behavior Description | Status | Current Test Scenario | Gap / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **TOPIC-01** | `TOPIC` query when unset | **COVERED** | `21_topic_query_and_persistence.spec` | Verified `331 RPL_NOTOPIC`. |
| **TOPIC-02** | `TOPIC` query when set | **COVERED** | `21_topic_query_and_persistence.spec` | Verified `332 RPL_TOPIC`. |
| **TOPIC-03** | `TOPIC` modification by op | **COVERED** | `08_channel_topic.spec`, `21_topic_query_and_persistence.spec` | Verified broadcast to all members. |
| **TOPIC-04** | `TOPIC` non-op with `+t` (denied) | **COVERED** | `08_channel_topic.spec`, `21_topic_query_and_persistence.spec` | Verified `482 ERR_CHANOPRIVSNEEDED`. |
| **TOPIC-05** | `TOPIC` non-op with `-t` (allowed) | **COVERED** | `18_mode_queries_and_removal.spec` | Verified non-op can set topic when `-t`. |
| **TOPIC-06** | `TOPIC` clear / unset (`:`) | **COVERED** | `31_topic_clearing_and_errors.spec` | Verified `TOPIC #chan :` clears topic and subsequent query returns `331`. |
| **TOPIC-07** | `TOPIC` user not on channel | **COVERED** | `31_topic_clearing_and_errors.spec` | Verified `TOPIC #chan` when not in channel returns `442 ERR_NOTONCHANNEL`. |
| **TOPIC-08** | `TOPIC` nonexistent channel | **COVERED** | `31_topic_clearing_and_errors.spec` | Verified `TOPIC #nonexistent` returns `403 ERR_NOSUCHCHANNEL`. |

---

### Category 7: Operator Commands: `KICK` & `INVITE` (OPCMD)

| ID | Behavior Description | Status | Current Test Scenario | Gap / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **OPCMD-01** | `KICK` by op with reason | **COVERED** | `05_invite_and_kick.spec`, `17_kick_cleanup.spec` | Target ejected and broadcast received. |
| **OPCMD-02** | `KICK` by op without reason | **COVERED** | `32_kick_and_invite_edge_cases.spec` | Verified `KICK #chan target` without trailing reason broadcasts kick. |
| **OPCMD-03** | `KICK` by non-op (denied) | **COVERED** | `09_channel_operator_privs.spec` | Verified `482 ERR_CHANOPRIVSNEEDED`. |
| **OPCMD-04** | `KICK` target not in channel | **COVERED** | `32_kick_and_invite_edge_cases.spec` | Verified `KICK #chan nonmember` returns `441 ERR_USERNOTINCHANNEL`. |
| **OPCMD-05** | `KICK` sender not in channel | **COVERED** | `32_kick_and_invite_edge_cases.spec` | Verified non-member sending `KICK` returns `442 ERR_NOTONCHANNEL`. |
| **OPCMD-06** | `KICK` nonexistent channel | **COVERED** | `32_kick_and_invite_edge_cases.spec` | Verified `KICK #fake target` returns `403 ERR_NOSUCHCHANNEL`. |
| **OPCMD-07** | `KICK` missing parameters | **COVERED** | `32_kick_and_invite_edge_cases.spec` | Verified `KICK` with no args returns `461 ERR_NEEDMOREPARAMS`. |
| **OPCMD-08** | `INVITE` standard operation | **COVERED** | `05_invite_and_kick.spec` | Verified `341 RPL_INVITING` & invite notice. |
| **OPCMD-09** | `INVITE` on `+i` channel bypass | **COVERED** | `05_invite_and_kick.spec` | Invited client successfully joins `+i` channel. |
| **OPCMD-10** | `INVITE` on `+i` by non-op | **COVERED** | `32_kick_and_invite_edge_cases.spec` | Verified non-op attempting `INVITE` on `+i` returns `482 ERR_CHANOPRIVSNEEDED`. |
| **OPCMD-11** | `INVITE` user already in channel | **COVERED** | `32_kick_and_invite_edge_cases.spec` | Verified inviting existing member returns `443 ERR_USERONCHANNEL`. |
| **OPCMD-12** | `INVITE` nonexistent user | **COVERED** | `20_invite_errors.spec` | Verified `401 ERR_NOSUCHNICK`. |
| **OPCMD-13** | `INVITE` sender not in channel | **COVERED** | `20_invite_errors.spec` | Verified `442 ERR_NOTONCHANNEL`. |

---

### Category 8: Channel Modes (MODE)

| ID | Behavior Description | Status | Current Test Scenario | Gap / Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **MODE-01** | Query channel mode | **COVERED** | `18_mode_queries_and_removal.spec` | Verified `324 RPL_CHANNELMODEIS`. |
| **MODE-02** | Mode edit by non-op | **COVERED** | `33_mode_demotion_and_chained.spec` | Verified non-op member sending `MODE #chan +i` returns `482`. |
| **MODE-03** | Mode `+i` (Invite-Only) | **COVERED** | `05_invite_and_kick.spec`, `18_mode_queries_and_removal.spec` | Blocks join (`473`), unblocks on invite. |
| **MODE-04** | Mode `-i` (Remove Invite-Only)| **COVERED** | `18_mode_queries_and_removal.spec` | Unblocks join for any user. |
| **MODE-05** | Mode `+t` (Topic Lock) | **COVERED** | `08_channel_topic.spec`, `18_mode_queries_and_removal.spec` | Blocks non-op topic changes (`482`). |
| **MODE-06** | Mode `-t` (Remove Topic Lock)| **COVERED** | `18_mode_queries_and_removal.spec` | Permits non-op topic changes. |
| **MODE-07** | Mode `+k` (Channel Key) | **COVERED** | `06_channel_key.spec`, `18_mode_queries_and_removal.spec` | Enforces key on join (`475`). |
| **MODE-08** | Mode `-k` (Remove Key) | **COVERED** | `18_mode_queries_and_removal.spec` | Removes key requirement. |
| **MODE-09** | Mode `+o` (Grant Operator) | **COVERED** | `09_channel_operator_privs.spec`, `33_mode_demotion_and_chained.spec` | Grants operator capabilities (`@`). |
| **MODE-10** | Mode `-o` (Revoke Operator) | **COVERED** | `33_mode_demotion_and_chained.spec` | Op revokes op from another op (`-o`); target loses op capabilities. |
| **MODE-11** | Mode `+o`/`-o` on non-member | **COVERED** | `33_mode_demotion_and_chained.spec` | Verified `MODE #chan +o nonmember` returns `441 ERR_USERNOTINCHANNEL`. |
| **MODE-12** | Mode `+l` (User Limit) | **COVERED** | `07_channel_limit.spec`, `18_mode_queries_and_removal.spec` | Blocks join when full (`471`). |
| **MODE-13** | Mode `-l` (Remove Limit) | **COVERED** | `18_mode_queries_and_removal.spec` | Allows joining beyond previous limit. |
| **MODE-14** | Mode `+l` invalid/non-numeric | **COVERED** | `33_mode_demotion_and_chained.spec` | Verified `MODE #chan +l -5` / `invalidlimit` handled gracefully. |
| **MODE-15** | Multi-mode chained flags | **COVERED** | `33_mode_demotion_and_chained.spec` | Verified `MODE #chan +it` applied and broadcast. |
| **MODE-16** | Unknown mode flag | **COVERED** | `19_mode_errors.spec` | Verified `472 ERR_UNKNOWNMODE`. |

---

## 3. Test Suite Complete Scenario Mapping

All 67 itemized behaviors from RFC 1459/2812 are mapped and covered across the 33 `.spec` files in `/home/tbatis/core/berg/tester/scenarios/`:

- **Networking**: `02_fragmentation.spec`, `13_command_case_and_fragmentation.spec`, `22_abrupt_close_and_reconnect.spec`, `23_pause_and_bounded_flood.spec`, `27_framing_and_delimiters.spec`, `28_high_concurrency_multiplexing.spec`
- **Registration**: `01_pass_failure.spec`, `11_parameter_errors.spec`, `12_duplicate_nick_recovery.spec`, `25_registration_gating_and_modes.spec`, `26_dynamic_nick_change_and_errors.spec`
- **Lifecycle**: `10_client_disconnect.spec`, `24_ping_pong_and_quit.spec`
- **Membership**: `04_channel_join_and_broadcast.spec`, `16_part_and_rejoin.spec`, `17_kick_cleanup.spec`, `29_membership_and_param_errors.spec`
- **Messaging**: `03_basic_registration_and_privmsg.spec`, `14_negative_targets.spec`, `15_recipient_isolation.spec`, `30_msg_edge_cases_and_formatting.spec`
- **Topic**: `08_channel_topic.spec`, `21_topic_query_and_persistence.spec`, `31_topic_clearing_and_errors.spec`
- **Invite & Kick**: `05_invite_and_kick.spec`, `20_invite_errors.spec`, `32_kick_and_invite_edge_cases.spec`
- **Channel Modes**: `06_channel_key.spec`, `07_channel_limit.spec`, `09_channel_operator_privs.spec`, `18_mode_queries_and_removal.spec`, `19_mode_errors.spec`, `33_mode_demotion_and_chained.spec`
