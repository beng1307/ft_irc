# IRC Server Edge Cases & Failure Scenarios Breakdown

This document provides a comprehensive, code-tailored catalog of edge cases, socket failure modes, race conditions, parser boundary cases, and IRC protocol state combinations tailored specifically to the implementation in `Server/`, `Client/`, and `Channel/`.

---

## 1. Network, Socket & OS Level Failure Scenarios

### 1.1. Send to a Closed / Crashed Client Socket (`EPIPE` / `ECONNRESET`)
* **Specific Code Path:** `ServerMessaging.cpp::send_string()`, `Channel::broadcast_from()`, `ServerLoop.cpp::poll()`
* **Scenario:** Client A, B, and C are in `#channel`. Client C abruptly terminates (`kill -9` or TCP RST). Client A sends `PRIVMSG #channel :hello`.
* **Mechanism:** `send_string()` calls `send(fd, ..., MSG_NOSIGNAL)`. `MSG_NOSIGNAL` prevents `SIGPIPE` crash, but `send()` returns `-1`. In the current codebase, `send_string` ignores the return code. Client C remains in `clients` map and `member_fds` until `poll()` catches `POLLERR`/`POLLHUP` or `recv()` returns 0.
* **Risk / Behavior:** Server must not crash, and must cleanly sweep the dead FD on the next poll cycle without corrupting channel member lists.

### 1.2. Non-Blocking Send Buffer Saturation (`EAGAIN` / `EWOULDBLOCK`)
* **Specific Code Path:** `ServerSocket.cpp::configure_socket_nonblocking()`, `ServerMessaging.cpp::send_string()`
* **Scenario:** Client A has a high-latency connection or suspends execution (`kill -STOP`). Another client floods large channel messages or large `NAMES` replies.
* **Mechanism:** With non-blocking sockets, when kernel buffer fills up, `send()` returns `-1` with `EAGAIN`/`EWOULDBLOCK` or performs a partial write.
* **Risk / Behavior:** Without write buffers or `POLLOUT` monitoring, un-sent bytes are silently dropped or truncated.

### 1.3. Simultaneous `POLLHUP` and `POLLIN` Event Resolution
* **Specific Code Path:** `ServerLoop.cpp::server_loop()` lines 128–140
* **Scenario:** Client sends `QUIT :Leaving now\r\n` and immediately invokes `close()`.
* **Mechanism:** `poll()` returns with both `POLLIN` and `POLLHUP` set in `revents`. The loop checks `(POLLERR | POLLHUP | POLLNVAL)` before `POLLIN`, which triggers `disconnect_client()` immediately before `handle_client_input()` can consume the pending quit reason from the socket buffer.

### 1.4. Operating System File Descriptor Reuse
* **Specific Code Path:** `ServerLoop.cpp::accept_new_client()`, `Server::add_client()`
* **Scenario:** Client A on FD 4 disconnects. Client B connects immediately and is assigned FD 4 by the kernel.
* **Mechanism:** If Client A's cleanup in any channel (`member_fds`, `operator_fds`, `invited_fds`) had any lingering entry, Client B on reused FD 4 could inherit stale privileges.

---

## 2. Buffer Management, Framing & Malformed Streams

### 2.1. TCP Stream Fragmentation Across Command Boundaries
* **Specific Code Path:** `ServerLoop.cpp::handle_client_input()`, `Client::get_buffer()`
* **Scenario:** Client stream is fragmented across arbitrary packet boundaries:
  - Packet 1: `NICK al`
  - Packet 2: `ice\r\nUSER alice 0 * :Alice`
  - Packet 3: ` Smith\r\n`
* **Mechanism:** `recv()` appends chunks to `client.get_buffer()`. Loop searches for `\r\n`, slices complete command, removes processed bytes, and maintains remaining partial bytes.

### 2.2. Command Pipelining with Embedded `QUIT`
* **Specific Code Path:** `ServerLoop.cpp::handle_client_input()`, `ServerCommands.cpp::handle_quit_command()`
* **Scenario:** Client sends multiple commands in a single TCP frame:
  `PASS 1234\r\nNICK alice\r\nUSER alice 0 * :Alice\r\nQUIT :bye\r\nJOIN #test\r\n`
* **Mechanism:** `handle_quit_command()` executes and calls `disconnect_client(client_fd)`. The while loop in `handle_client_input()` checks `if (!get_client(client_fd)) return;` to avoid use-after-free or operating on the erased client.

### 2.3. Buffer Bomb / Slowloris (Data Stream Without CRLF)
* **Specific Code Path:** `ServerLoop.cpp::handle_client_input()`
* **Scenario:** Client streams continuous bytes without ever sending `\r\n`.
* **Mechanism:** `client.get_buffer().append()` continues growing without truncation until a line delimiter is received.

### 2.4. Bare Delimiters & Linefeed Variants (`\n`, `\r\r\n`, `\r\n\r\n`)
* **Specific Code Path:** `ServerCommands.cpp::handle_line()`
* **Scenario:**
  - Bare `\n`: Ignored / buffered waiting for `\r\n` (RFC 1459/2812 strict delimiter).
  - Extra carriage return `\r\r\n`: Resulting token contains `\r`, which fails nickname validation (`432`).
  - Consecutive `\r\n\r\n`: Empty line check safely discards without error response.

---

## 3. Client Registration & Authentication Matrix

### 3.1. Out-of-Order Registration Transitions
* **Specific Code Path:** `ServerCommands.cpp::dispatch_command()`, `ServerHelper.cpp::try_register_client()`
* **State Matrix:**
  - `NICK` -> `USER` -> `PASS`: Client registers on `PASS`.
  - `USER` -> `PASS` -> `NICK`: Client registers on `NICK`.
  - `PASS` -> `USER` -> `NICK`: Client registers on `NICK`.
  - `USER` -> `NICK` (no `PASS`): Client remains unregistered; subsequent commands receive `451 :You have not registered`.

### 3.2. Reregistration Lock
* **Specific Code Path:** `ServerCommands.cpp::handle_pass_command()`, `ServerCommands.cpp::handle_user_command()`
* **Scenario:** Registered client sends `PASS` or `USER`.
* **Outcome:** Server rejects with `462 :You may not reregister`.

### 3.3. Unauthenticated Nickname Collision / Takeover
* **Specific Code Path:** `ServerCommands.cpp::handle_nick_command()` lines 160–167
* **Scenario:** Client 1 sends only `NICK alice` (without `PASS`). Client 2 connects, sends valid `PASS 1234` and `NICK alice`.
* **Mechanism:** `handle_nick_command()` checks `(existing_client.get_register_status() || existing_client.get_pass_ok())`. If Client 1 has neither, Client 2 claims `alice`.

---

## 4. Channel Lifecycle & Mode Edge Cases

### 4.1. Channel Operator Depletion (Orphaned Channels)
* **Specific Code Path:** `ServerCommands.cpp::part_client_from_channel()`, `ServerLoop.cpp::disconnect_client()`
* **Scenario:** Client A (sole operator) and Client B (regular member) are in `#chan`. Client A parts or disconnects.
* **Outcome:** `#chan` remains active with Client B. Channel has 0 operators. Non-operator actions (topic changes under `+t`, mode changes, invites under `+i`, kicks) fail with `482 :You're not channel operator`.

### 4.2. Operator Self-Demotion & Self-Kick
* **Specific Code Path:** `ServerChannelOps.cpp::handle_mode()`, `ServerChannelOps.cpp::handle_kick()`
* **Scenario:**
  - Self-Demotion: Operator sends `MODE #chan -o self`. Operator status removed; channel enters op-less state if no other ops exist.
  - Self-Kick: Operator sends `KICK #chan self :bye`. Operator is kicked from channel; channel destroyed if empty.

### 4.3. Chained & Mixed Mode Strings
* **Specific Code Path:** `ServerChannelOps.cpp::handle_mode()`
* **Scenario:** Operator sends `MODE #chan +itk-l+o secret target_nick`.
* **Mechanism:** State machine updates sign (`+`/`-`), applies boolean flags (`i`, `t`), extracts parameters for `k` and `o`, removes limit `l`, and formats single broadcast message.

### 4.4. Channel Access Rejection Precedence (`+i`, `+k`, `+l`)
* **Specific Code Path:** `ServerCommands.cpp::let_client_join_channel()` lines 41–59
* **Scenario:** Channel has `+i` (invite-only), `+k secret` (key), and `+l 1` (full).
* **Evaluation Order:**
  1. Invite check -> `473 :Cannot join channel (+i)`
  2. Key check -> `475 :Cannot join channel (+k)`
  3. Limit check -> `471 :Cannot join channel (+l)`

---

## 5. Messaging & Audience Scenarios

### 5.1. Multi-Channel Audience Deduplication
* **Specific Code Path:** `ServerMessaging.cpp::get_client_audience()`, `ServerCommands.cpp::handle_nick_command()`
* **Scenario:** Client A and Client B share 3 mutual channels. Client A changes nickname or quits.
* **Mechanism:** `get_client_audience()` aggregates peer FDs across mutual channels and deduplicates them using `Set<int>`. Client B receives exactly 1 broadcast.

### 5.2. PRIVMSG Routing Matrix
* **Specific Code Path:** `ServerMessaging.cpp::send_message_to_user()`, `ServerMessaging.cpp::send_message_to_channel()`
* **Scenario Matrix:**
  - Non-existent nick: `401 <nick> :No such nick/channel`
  - Non-existent channel: `403 <chan> :No such channel`
  - User not in target channel: `442 <chan> :You're not on that channel`
  - Empty message payload: `412 :No text to send`
  - No recipient: `411 :No recipient given (PRIVMSG)`
  - Message containing multiple colons (`:foo: bar: baz`): Line after first `" :"` preserved completely.

### 5.3. TOPIC Query vs Set vs Clear Lifecycle
* **Specific Code Path:** `ServerChannelOps.cpp::handle_topic()`
* **Scenario Matrix:**
  - `TOPIC #chan` (no colon): Queries topic (`331` if empty, `332` if set).
  - `TOPIC #chan :New Topic`: Sets topic and broadcasts to channel.
  - `TOPIC #chan :`: Clears topic (`""`) and broadcasts empty topic to channel.
  - Non-operator set under `+t`: Returns `482 :You're not channel operator`.

---

## 8. High Concurrency & Microsecond Race Conditions

### 8.1. Simultaneous Nickname Collision Race
* **Specific Code Path:** `ServerCommands.cpp::handle_nick_command()`, `ServerHelper.cpp::is_nickname_in_use()`
* **Scenario:** 50 OS threads establish TCP connections and synchronize via `pthread_barrier_t`. Upon release, all 50 threads simultaneously submit `PASS <pass>\r\nNICK winner\r\nUSER winner 0 * :winner\r\n`.
* **Mechanism:** Single-threaded `poll()` event loop must serialize nickname claims atomically.
* **Outcome:** Exactly 1 thread successfully registers and receives `001 RPL_WELCOME` with nickname `winner`. The remaining 49 threads are rejected with numeric `433 :Nickname is already in use` without crash, hang, or race leakage.

### 8.2. Simultaneous Channel Mode & Join Race
* **Specific Code Path:** `ServerCommands.cpp::let_client_join_channel()`, `ServerChannelOps.cpp::handle_mode()`
* **Scenario:** 20 registered client threads synchronize via barrier and simultaneously execute `JOIN #race` and attempt mode modifications (`MODE #race +k secret` or `MODE #race +i`).
* **Mechanism:** The first client processed creates `#race` and gains operator status (`+o`). Subsequent client joins either complete prior to mode change or receive `475 :Cannot join channel (+k)` / `473 :Cannot join channel (+i)`. Non-operator mode modification attempts are rejected with `482 :You're not channel operator` or `442 :You're not on that channel`.
* **Outcome:** Member lists and mode states remain internally coherent, prevent privilege escalation, and cause no memory corruption or deadlocks.

### 8.3. Burst Accept Queue Saturation
* **Specific Code Path:** `ServerSocket.cpp::socket_setup()`, `ServerLoop.cpp::server_loop()`, `ServerLoop.cpp::accept_new_client()`
* **Scenario:** 100 threads initiate TCP connections simultaneously within a 10ms burst window.
* **Outcome:** Server event loop processes all pending connections from the listen backlog without dropping clients or starving the event loop.

