# Comprehensive QUIT Command Flow, Adversarial Analysis & Test Inventory

This document provides an exhaustive, line-by-line breakdown of the `QUIT` command lifecycle and client disconnection mechanics in `ft_irc`. It details input grammar edge cases, state transitions, client/channel cleanup mechanics, buffer draining semantics, socket cleanup, command pipelining, ghost state risks, operator succession, multi-channel audience calculations, error handling, adversarial attack vectors, and reachable failure modes.

---

## 1. Flow Overview & Architecture

### High-Level Architecture Flowchart
```
                      [Client sends QUIT [:reason]]
                                    │
                                    ▼
                      Server::handle_client_input (recv up to 512 bytes)
                                    │
                                    ▼
                      Server::handle_line (extracts line delimited by \r\n)
                                    │
                                    ▼
                      Server::split_arguments (extracts tokens & trailing :)
                                    │
                                    ▼
                      Server::dispatch_command
                                    │
                         command == "QUIT" ?
                                    │
                                   Yes
                                    ▼
                      Server::handle_quit_command
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
Extract Reason:                                     Calculate Audience:
- If arguments.empty() -> "Leaving server"          get_client_audience(fd)
- Else -> arguments[0]                              - Iterates all server channels
                                                    - Unions members of mutual channels
                                                    - Subtracts quitting client fd
         │                                                     │
         └──────────────────────────┬──────────────────────────┘
                                    ▼
         Broadcast to Audience (Set<int>):
         make_msg(client, "QUIT", ":" + reason)
         -> Sent to every unique peer sharing >= 1 channel
                                    │
                                    ▼
         Send to Quitting Client:
         client.should_disconnect(true)
         client.send("ERROR :Closing connection")
                                    │
                                    ▼
         Server::send_to_client(fd, message)
                                    │
                 ┌──────────────────┴──────────────────┐
                 ▼                                     ▼
        [Write Succeeds &                     [Partial Write or EAGAIN]
         out_buffer is Empty]                 - out_buffer contains unsent data
                 │                            - set_pollout(fd, true)
                 ▼                            - Socket remains open waiting for POLLOUT
         Server::disconnect_client(fd)                 │
                 │                                     ▼
                 │                            [POLLOUT fires later & drains out_buffer]
                 │                                     │
                 └──────────────────┬──────────────────┘
                                    ▼
                      Server::disconnect_client(fd)
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
Channel Cleanup:             Clients Map:               Poll Descriptors:
- remove_invited(fd)         remove_client(fd)          - Erases fd from _fds vector
- remove_member(fd)          (erases Client object)     - close(fd)
- promote_first_member_                                 (releases file descriptor)
  if_no_operators()
- Erases empty channels
```

---

## 2. Line-by-Line Code Breakdown by Component

### A. Command Dispatch & Reason Parsing (`ServerCommands.cpp`, `ServerHelper.cpp`)

#### 1. Unregistered Client Disconnection
- **Code Reference**: `ServerCommands.cpp:286-314`
  - `QUIT` is checked *before* `!client.get_register_status()`.
  - Unregistered clients (e.g. connected but sent invalid password, or disconnected before finishing handshake) can send `QUIT` without triggering `451 ERR_NOTREGISTERED`.
  - `get_client_audience` returns an empty set since unregistered clients are in 0 channels. No broadcast is made.
  - Client receives `ERROR :Closing connection` and socket is cleanly closed.

#### 2. Reason Parsing & Trailing Parameter Handling
- **Code Reference**: `ServerCommands.cpp:258-271` & `ServerHelper.cpp:62-91`
  - `QUIT` (no arguments) $\to$ `reason` defaults to `"Leaving server"`. Broadcast: `:Alice!* QUIT :Leaving server`.
  - `QUIT ` (trailing whitespace) $\to$ trims trailing whitespace $\to$ defaults to `"Leaving server"`.
  - `QUIT :Leaving for lunch` $\to$ `arguments[0]` is `"Leaving for lunch"` $\to$ Broadcast: `:Alice!* QUIT :Leaving for lunch`.
  - `QUIT :` (empty colon argument) $\to$ `reason` is `""`. Broadcast: `:Alice!* QUIT :`.
  - `QUIT ::)` (reason starting with colon / emoji) $\to$ `reason` is `":)"`. Broadcast: `:Alice!* QUIT ::)`.
  - `QUIT Goodbye everyone!` (multi-word without leading colon) $\to$ `arguments[0] = "Goodbye"`, remaining words discarded per standard token splitting.
  - `QUIT :   spaced reason   ` $\to$ preserves internal spaces after leading colon.

---

### B. Event Loop, Asynchronous I/O, & Disconnect Semantics (`ServerLoop.cpp`)

#### 1. Delayed Disconnection via `client.should_disconnect(true)`
- **Code Reference**: `ServerLoop.cpp:110-152`
  - `handle_quit_command` sets `client.should_disconnect(true)` and calls `client.send(bye)`.
  - If the socket is writable and output buffer empties immediately, `disconnect_client(fd)` executes synchronously.
  - If the kernel socket buffer is full (or slow client), `set_pollout(fd, true)` arms `POLLOUT` in the poll loop. Disconnection occurs once the output buffer drains or 1MB SendQ limit is exceeded.

#### 2. Pipelined Ghost Command Execution Prevention
- **Code Reference**: `ServerLoop.cpp:175-185`
  - When commands arrive pipelined in a single TCP packet (`QUIT :bye\r\nPRIVMSG #chan :ghost\r\n`), `handle_client_input` verifies `if (!get_client(client_fd))` after each line. Once disconnected, subsequent commands are dropped immediately.

#### 3. Abrupt Disconnect (EOF / RST / recv() == 0)
- **Code Reference**: `ServerLoop.cpp:160-191`
  - An abrupt socket close triggers `disconnect_client(fd)` immediately, releasing resources, channels, and descriptors without hanging.

---

### C. Multi-Channel Cleanup, Operator Succession & Security (`ServerMessaging.cpp`, `ServerLoop.cpp`, `Channel.cpp`)

#### 1. Deduplicated Audience Calculation
- **Code Reference**: `ServerMessaging.cpp:146-156`
  - `get_client_audience` computes `Set<int>` across all mutual channels, subtracting the sender FD. Peers sharing multiple channels receive the notification exactly once.

#### 2. Channel Cleanup & Operator Succession
- **Code Reference**: `ServerLoop.cpp:62-88` & `Channel.cpp:145-150`
  - **Invited FD Cleanup**: `remove_invited(client_fd)` cleans pending invitations, preventing the **Ghost Invite Vulnerability** on recycled FDs.
  - **Auto-Promotion**: When the sole channel operator quits, `promote_first_member_if_no_operators()` promotes the next member so channels are never orphaned.
  - **Empty Channel GC**: Channels left with 0 members are deleted from `_channels`.
  - **Nickname Release**: Nickname is immediately freed in `remove_client(client_fd)`.

---

## 3. Adversarial & Malicious Attack Vectors

| Attack Vector | Malicious Scenario | Defensive Mechanism in Code | Verification Spec |
| :--- | :--- | :--- | :--- |
| **ADV-QUIT-01: Line Flood Overflow** | Attacker sends > 512 bytes in a single line without `\r\n`. | `input_exceeds_irc_line_limit` detects overflow and forcibly closes connection before memory exhaustion. | [`251_QUIT_oversized_line_flood_overflow.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/251_QUIT_oversized_line_flood_overflow.spec) |
| **ADV-QUIT-02: Boundary Line (510B)** | Attacker sends max RFC payload (510 bytes). | Handled cleanly without truncation or buffer corruption. | [`250_QUIT_line_length_boundary_510_bytes.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/250_QUIT_line_length_boundary_510_bytes.spec) |
| **ADV-QUIT-03: Ghost Invite FD Reuse** | Attacker gets invited to `+i` channel, quits, reconnects on recycled FD. | `disconnect_client` purges FD from `invited_fds`; unauthorized entry is blocked with `473`. | [`239_QUIT_invited_fd_cleanup.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/239_QUIT_invited_fd_cleanup.spec) |
| **ADV-QUIT-04: Channel User Limit Churn** | Channel is full (`+l 2`); member quits. | Member count accurately decrements, allowing blocked clients to enter. | [`246_QUIT_channel_user_limit_decrement.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/246_QUIT_channel_user_limit_decrement.spec) |
| **ADV-QUIT-05: Spoofed Prefix Injection** | Attacker sends `:Bob QUIT :Spoofed`. | Server rejects client-supplied prefixes with `421 Unknown command.` | [`254_QUIT_spoofed_prefix_rejection.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/254_QUIT_spoofed_prefix_rejection.spec) |
| **ADV-QUIT-06: Cascading Multi-Op Drop** | Op is sole op in 2 channels and sole member in 1 channel. | Promotes remaining members in active channels and destroys empty channel without iterator corruption. | [`252_QUIT_cascading_multi_channel_op_destruction.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/252_QUIT_cascading_multi_channel_op_destruction.spec) |
| **ADV-QUIT-07: Rapid Nick Hijacking Race** | Client connects, quits, and immediately reconnects claiming same nick in rapid loop. | `remove_client` releases nickname synchronously, allowing seamless re-registration without `433` collision. | [`253_QUIT_rapid_reconnect_same_nick_burst.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/253_QUIT_rapid_reconnect_same_nick_burst.spec) |
| **ADV-QUIT-08: Self-Demotion Op Recovery** | Sole op de-ops self (`MODE -o`), then quits. | `disconnect_client` calls `promote_first_member_if_no_operators()`, restoring operability. | [`249_QUIT_demote_self_then_quit_opless_recovery.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/249_QUIT_demote_self_then_quit_opless_recovery.spec) |
| **ADV-QUIT-09: Post-QUIT PRIVMSG Target** | Sender transmits PRIVMSG to user who just sent QUIT. | Returns `401 ERR_NOSUCHNICK` safely without SIGPIPE or dead socket write panics. | [`248_QUIT_privmsg_to_just_quitted_client.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/248_QUIT_privmsg_to_just_quitted_client.spec) |
| **ADV-QUIT-10: Mode & Topic Retention** | Op sets `+k`, `+t`, and topic before quitting. | Channel retains keys, modes, and topics under the promoted operator. | [`247_QUIT_modes_and_topic_persistence_after_op_quit.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/247_QUIT_modes_and_topic_persistence_after_op_quit.spec) |

---

## 4. Complete Test Spec Inventory (`tester/scenarios/commands/QUIT/`)

| Spec Number & Name | Scenario Summary |
| :--- | :--- |
| [`226_QUIT_bare_no_arguments.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/226_QUIT_bare_no_arguments.spec) | Bare `QUIT` defaults to `"Leaving server"` reason and cleanly disconnects. |
| [`227_QUIT_trailing_whitespace.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/227_QUIT_trailing_whitespace.spec) | `QUIT   ` with trailing spaces trims to default reason. |
| [`228_QUIT_colon_with_reason.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/228_QUIT_colon_with_reason.spec) | Multi-word trailing colon reason (`QUIT :Leaving for lunch with colleagues`). |
| [`229_QUIT_empty_colon_reason.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/229_QUIT_empty_colon_reason.spec) | Empty colon parameter (`QUIT :`) broadcasts empty trailing colon. |
| [`230_QUIT_colon_with_whitespace.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/230_QUIT_colon_with_whitespace.spec) | Whitespace preserved in reason payload (`QUIT :   spaces preserved   `). |
| [`231_QUIT_colon_in_reason_emoji.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/231_QUIT_colon_in_reason_emoji.spec) | Colons in smilies/reasons (`QUIT ::)`) preserved intact. |
| [`232_QUIT_multi_word_without_colon.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/232_QUIT_multi_word_without_colon.spec) | Space-separated reasons without colon (`QUIT Goodbye everyone!`) isolate first token. |
| [`233_QUIT_unregistered_client.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/233_QUIT_unregistered_client.spec) | Unregistered client sends `QUIT` without triggering `451 ERR_NOTREGISTERED`. |
| [`234_QUIT_after_wrong_pass.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/234_QUIT_after_wrong_pass.spec) | Failed authentication followed by `QUIT` terminates cleanly. |
| [`235_QUIT_multi_channel_broadcast.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/235_QUIT_multi_channel_broadcast.spec) | Deduplicated broadcast across overlapping shared channels (`#c1`, `#c2`, `#c3`). |
| [`236_QUIT_audience_self_exclusion.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/236_QUIT_audience_self_exclusion.spec) | Quitter receives ERROR, not own QUIT echo. |
| [`237_QUIT_sole_member_channel_destroyed.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/237_QUIT_sole_member_channel_destroyed.spec) | Channel destroyed on sole member QUIT; recreated fresh on next join. |
| [`238_QUIT_sole_operator_auto_promotion.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/238_QUIT_sole_operator_auto_promotion.spec) | Sole operator QUIT auto-promotes next member to operator. |
| [`239_QUIT_invited_fd_cleanup.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/239_QUIT_invited_fd_cleanup.spec) | Pending invite wiped on target QUIT, preventing recycled FD bypass. |
| [`240_QUIT_immediate_nick_reuse.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/240_QUIT_immediate_nick_reuse.spec) | Nickname freed immediately upon QUIT for new client connection. |
| [`241_QUIT_pipelined_stream_abort.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/241_QUIT_pipelined_stream_abort.spec) | Pipelined commands following QUIT in a single TCP frame are dropped. |
| [`242_QUIT_part_then_quit_no_leak.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/242_QUIT_part_then_quit_no_leak.spec) | PART then QUIT sends no duplicate QUIT broadcast to ex-channel members. |
| [`243_QUIT_kick_then_quit_isolation.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/243_QUIT_kick_then_quit_isolation.spec) | Kicked client sending QUIT does not broadcast to the kicked channel. |
| [`244_QUIT_rapid_connect_quit_burst.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/244_QUIT_rapid_connect_quit_burst.spec) | High frequency connect/join/quit stress test. |
| [`245_QUIT_case_insensitivity.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/245_QUIT_case_insensitivity.spec) | Lowercase (`quit`) and mixed-case (`QuiT`) dispatch. |
| [`246_QUIT_channel_user_limit_decrement.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/246_QUIT_channel_user_limit_decrement.spec) | User limit (+l) occupancy decrements on QUIT, allowing blocked clients to enter. |
| [`247_QUIT_modes_and_topic_persistence_after_op_quit.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/247_QUIT_modes_and_topic_persistence_after_op_quit.spec) | Channel modes (+k, +t) and topic persist under auto-promoted operator. |
| [`248_QUIT_privmsg_to_just_quitted_client.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/248_QUIT_privmsg_to_just_quitted_client.spec) | PRIVMSG to recently quitted client returns `401 ERR_NOSUCHNICK` cleanly. |
| [`249_QUIT_demote_self_then_quit_opless_recovery.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/249_QUIT_demote_self_then_quit_opless_recovery.spec) | Sole op de-ops self, then quits; next member auto-promoted. |
| [`250_QUIT_line_length_boundary_510_bytes.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/250_QUIT_line_length_boundary_510_bytes.spec) | Large QUIT payload up to RFC line length limit handled safely. |
| [`251_QUIT_oversized_line_flood_overflow.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/251_QUIT_oversized_line_flood_overflow.spec) | Oversized line (>512 bytes) flood triggers disconnect protection. |
| [`252_QUIT_cascading_multi_channel_op_destruction.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/252_QUIT_cascading_multi_channel_op_destruction.spec) | Multi-channel cascading operator promotion and empty channel destruction. |
| [`253_QUIT_rapid_reconnect_same_nick_burst.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/253_QUIT_rapid_reconnect_same_nick_burst.spec) | Rapid consecutive reconnects claiming same nickname without collision. |
| [`254_QUIT_spoofed_prefix_rejection.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/QUIT/254_QUIT_spoofed_prefix_rejection.spec) | Spoofed client-prefix command rejected with `421 Unknown command.`. |
