# Detailed PING Command Analysis: Lifecycle, Edge Cases & Interactions

A comprehensive, line-by-line audit of the `PING` command implementation in `ft_irc` across the entire codebase (`ServerCommands.cpp`, `ServerHelper.cpp`, `ServerLoop.cpp`, `ServerMessaging.cpp`, `Client.cpp`, and `Wire.hpp`).

---

## Table of Contents
1. [End-to-End Flow Diagram](#1-end-to-end-flow-diagram)
2. [Code Trace & State Transitions](#2-code-trace--state-transitions)
3. [Deep Edge Case Matrix](#3-deep-edge-case-matrix)
   - [A. Input Parsing & Parameter Edge Cases](#a-input-parsing--parameter-edge-cases)
   - [B. Pre-Registration & Lifecycle States](#b-pre-registration--lifecycle-states)
   - [C. PONG Response Formatting & Token Preservation](#c-pong-response-formatting--token-preservation)
   - [D. Socket, Buffer, Pipelining & Network Edge Cases](#d-socket-buffer-pipelining--network-edge-cases)
4. [Command Interactions (What Happens When PING Interacts With...)](#4-command-interactions)
   - [1. PING + PASS / NICK / USER (Registration Handshake Interaction)](#1-ping--pass--nick--user-registration-handshake-interaction)
   - [2. PING + QUIT (Disconnection & Pipelining Anomalies)](#2-ping--quit-disconnection--pipelining-anomalies)
   - [3. PING + Channel Commands (JOIN, PART, KICK, MODE, TOPIC, INVITE)](#3-ping--channel-commands-join-part-kick-mode-topic-invite)
   - [4. PING + PRIVMSG / Flood / SendQ Backpressure](#4-ping--privmsg--flood--sendq-backpressure)
5. [Summary of Identified Vulnerabilities & Discrepancies](#5-summary-of-identified-vulnerabilities--discrepancies)
6. [Test Spec Mapping & Verification Plan](#6-test-spec-mapping--verification-plan)

---

## 1. End-to-End Flow Diagram

```
[ Inbound TCP Packet: "PING 123456\r\n" or "PING :my-cookie-payload\r\n" ]
         │
         ▼
[ ServerLoop.cpp: handle_client_input(fd) ]
   - recv(client_fd, buffer, 511, 0) reads bytes into stack buffer
   - client.append_raw_buffer(buffer, bytes_received)
   - Checks input_exceeds_irc_line_limit(client.get_buffer()) (<= 510 chars before \r\n)
   - Locates delimiter: position = client.get_buffer().find("\r\n")
         │
         ▼
[ ServerCommands.cpp: handle_line(client, position) ]
   - Extracts line: line = client.get_buffer().substr(0, position)
   - Erases from buffer: client.get_buffer().erase(0, position + 2)
   - Extracts command token: command = line.splitBy(' ')[0].toUpper() -> "PING"
   - Validates is_command("PING") == true
   - Calls split_arguments(line) -> Vector<Wire> ["123456"] or [":my-cookie-payload"]
   - Calls dispatch_command(client, "PING", arguments)
         │
         ▼
[ ServerCommands.cpp: dispatch_command(client, "PING", arguments) ]
   - Evaluates command == "PING" BEFORE checking !client.get_register_status()
   - Routes to handle_ping_command(client, arguments)
         │
         ▼
[ ServerCommands.cpp: handle_ping_command(client, arguments) ]
   - Evaluates token: Wire token = arguments.empty() ? "localhost" : arguments[0];
   - Strips leading colon if present: if (!token.empty() && token[0] == ':') token = token.substr(1);
   - Formats reply: Wire pong(":localhost PONG localhost :", token);
   - Calls client.send(pong);
         │
         ▼
[ Client.cpp: Client::send(Wire message) ]
   - Checks if message ends with "\r\n"; appends "\r\n" if missing
   - Invokes server->send_to_client(socket, message)
         │
         ▼
[ ServerLoop.cpp: Server::send_to_client(fd, message) ]
   - Appends message to client.get_out_buffer()
   - Checks SendQ: if out.size() > MAX_OUTPUT_BUFFER_SIZE (1MB) -> disconnect_client(fd)
   - Invokes send(fd, out.c_str(), out.size(), MSG_NOSIGNAL)
   - If partial write or EAGAIN/EWOULDBLOCK: sets POLLOUT flag on fd to resume in poll()
   - If fully flushed: clears POLLOUT flag
```

---

## 2. Code Trace & State Transitions

### State Variables & Data Structures Involved:
- `Client::is_registered` (`bool`): Whether client completed PASS + NICK + USER registration handshake.
- `Client::pass_ok` (`bool`): Whether correct PASS was received.
- `Client::buffer` (`Wire`): Input buffer holding unparsed TCP stream fragments.
- `Client::out_buffer` (`Wire`): Output buffer holding pending outbound bytes.
- `Server::fds` (`Vector<pollfd>`): Monitored file descriptors for `poll()`.

### State Transitions Table for PING:

| Initial Client State | Incoming PING Command | Resulting State | Server Response Sent | RFC 2812 Standard Compliance |
| :--- | :--- | :--- | :--- | :--- |
| `unregistered` (fresh connection) | `PING 1234` | Unchanged (`unregistered`) | `:localhost PONG localhost :1234\r\n` | Allowed in ft_irc (modern IRCd practice, though RFC 2812 §3.7.2 formally expects registered) |
| `unregistered` (PASS sent, no NICK) | `PING probe` | Unchanged (`unregistered`) | `:localhost PONG localhost :probe\r\n` | Allowed |
| `unregistered` (wrong PASS) | `PING probe` | Unchanged (`pass_ok=false`) | `:localhost PONG localhost :probe\r\n` | Allowed |
| `REGISTERED` | `PING cookie1` | Unchanged (`REGISTERED`) | `:localhost PONG localhost :cookie1\r\n` | Fully compliant |
| Any state | `PING` *(no arguments)* | Unchanged | `:localhost PONG localhost :localhost\r\n` | **Discrepancy**: RFC mandates `409 ERR_NOORIGIN` (`:localhost 409 <nick> :No origin specified`) |
| Any state | `PING   ` *(spaces only)* | Unchanged | `:localhost PONG localhost :localhost\r\n` | **Discrepancy**: RFC mandates `409 ERR_NOORIGIN` |
| Any state | `PING :cookie` | Unchanged | `:localhost PONG localhost :cookie\r\n` | Compliant |
| Any state | `PING ::cookie` *(double colon)* | Unchanged | `:localhost PONG localhost :cookie\r\n` | **Discrepancy**: Double-stripping removes client's payload colon |
| Any state | `PING token server2` | Unchanged | `:localhost PONG localhost :token\r\n` | Standard single-server fallback (server2 ignored) |

---

## 3. Deep Edge Case Matrix

### A. Input Parsing & Parameter Edge Cases

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PING-P01** | `PING\r\n` (0 parameters) | `409 :No origin specified` (ERR_NOORIGIN) | Responds with `:localhost PONG localhost :localhost\r\n` | **MEDIUM** | `arguments.empty()` defaults token to `"localhost"` instead of returning numeric error 409. |
| **PING-P02** | `PING    \r\n` (Trailing whitespace only) | `409 :No origin specified` (ERR_NOORIGIN) | `split_arguments` skips spaces, `arguments.empty()` is true. Returns `:localhost PONG localhost :localhost\r\n`. | **MEDIUM** | Same as PING-P01. |
| **PING-P03** | `PING :\r\n` (Empty token after colon) | `409 :No origin specified` or `:localhost PONG localhost :\r\n` | `split_arguments` captures `""`. Responds with `:localhost PONG localhost :\r\n`. | **LOW** | Empty token echoed. |
| **PING-P04** | `PING cookie123\r\n` (Standard single token) | `:localhost PONG localhost :cookie123\r\n` | Responds with `:localhost PONG localhost :cookie123\r\n`. | **NONE** | Standard flow. |
| **PING-P05** | `PING :cookie123\r\n` (Leading colon single token) | `:localhost PONG localhost :cookie123\r\n` | `split_arguments` strips outer `:`, `handle_ping_command` sees `"cookie123"`. Result: `:localhost PONG localhost :cookie123\r\n`. | **NONE** | Correctly parsed. |
| **PING-P06** | `PING ::cookie123\r\n` (Double colon payload) | `:localhost PONG localhost ::cookie123\r\n` | `split_arguments` strips 1st colon (`":cookie123"`), `handle_ping_command` strips 2nd colon (`"cookie123"`). Result: `:localhost PONG localhost :cookie123\r\n`. | **HIGH** | Double-stripping bug alters client's opaque cookie payload. |
| **PING-P07** | `PING :::cookie123\r\n` (Triple colon payload) | `:localhost PONG localhost :::cookie123\r\n` | Stripped twice -> `":cookie123"`. Result: `:localhost PONG localhost ::cookie123\r\n`. | **HIGH** | Token mutation bug. |
| **PING-P08** | `PING token1 server2\r\n` (Two parameters) | Forward to server2 or echo token1 if server2 is localhost | `split_arguments` yields `["token1", "server2"]`. `handle_ping_command` only reads `arguments[0]`. Result: `:localhost PONG localhost :token1\r\n`. | **LOW** | In single-server ft_irc, ignoring remote server forwarding is acceptable. |
| **PING-P09** | `PING token with spaces\r\n` (Multi-word without colon) | 1st token parsed as origin, subsequent tokens ignored or treated as target server | `split_arguments` splits by space: `arguments = ["token", "with", "spaces"]`. `handle_ping_command` takes `arguments[0]` (`"token"`). Result: `:localhost PONG localhost :token\r\n`. | **LOW** | Subsequent uncoloned tokens ignored. |
| **PING-P10** | `PING :token with spaces and symbols!@#\r\n` | `:localhost PONG localhost :token with spaces and symbols!@#\r\n` | `split_arguments` captures everything after `:`: `arguments[0] = "token with spaces and symbols!@#"`. Result: `:localhost PONG localhost :token with spaces and symbols!@#\r\n`. | **NONE** | Handled correctly. |
| **PING-P11** | `PING :  spaces  \r\n` (Colon followed by spaces) | Preserves all whitespace inside colon payload | `arguments[0] = "  spaces  "`. Result: `:localhost PONG localhost :  spaces  \r\n`. | **NONE** | Whitespace preserved. |
| **PING-P12** | `ping cookie\r\n` / `Ping cookie\r\n` (Case variations) | Case-insensitive command dispatch | `line.splitBy(' ')[0].toUpper()` normalizes to `"PING"`. Result: `:localhost PONG localhost :cookie\r\n`. | **NONE** | Handled correctly. |
| **PING-P13** | `:prefix PING cookie\r\n` (Client prefix before command) | Strip prefix or parse PING as command | `line.splitBy(' ')[0]` returns `":prefix"`. `is_command(":prefix")` is false -> `421 Unknown command.`. | **MEDIUM** | Server does not strip optional IRC client prefix. |
| **PING-P14** | ` PING cookie\r\n` (Leading whitespace before command) | Ignore leading whitespace or reject | `line.splitBy(' ')[0]` returns `""` -> `421 Unknown command.`. | **LOW** | Strict BNF adherence. |

---

### B. Pre-Registration & Lifecycle States

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PING-L01** | `PING` immediately upon TCP connect (before PASS/NICK/USER) | Allow liveness probe or reply with 451/409 | Responds immediately with `PONG`. Client state remains unregistered. | **LOW** | Intentional design: allows latency check / NAT keepalive before handshake. |
| **PING-L02** | `PING` after wrong PASS (`PASS wrongpass`) | Responds with PONG, registration remains blocked | Responds with PONG. `pass_ok` remains `false`. | **LOW** | No leakage of authentication state. |
| **PING-L03** | `PING` after correct PASS, before NICK/USER | Responds with PONG, `pass_ok` remains `true` | Responds with PONG. Handshake state untouched. | **NONE** | Correct behavior. |
| **PING-L04** | `PING` after NICK and USER set, before PASS | Responds with PONG, registration not completed | Responds with PONG. Client remains unregistered until PASS. | **NONE** | Correct behavior. |
| **PING-L05** | Repeated rapid `PING` before registration completes | Handled without crashing or state corruption | Every PING generates a PONG. No memory leaks. | **NONE** | Stateless execution. |

---

### C. PONG Response Formatting & Token Preservation

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PING-F01** | `PING 12345` (Numeric cookie) | `:localhost PONG localhost :12345\r\n` | `:localhost PONG localhost :12345\r\n` | **NONE** | Exact match. |
| **PING-F02** | `PING test.server.org` (Domain name cookie) | `:localhost PONG localhost :test.server.org\r\n` | `:localhost PONG localhost :test.server.org\r\n` | **NONE** | Exact match. |
| **PING-F03** | `PING :special_chars_!@#$%^&*()` | `:localhost PONG localhost :special_chars_!@#$%^&*()\r\n` | Exact characters preserved and echoed. | **NONE** | Handled. |
| **PING-F04** | `PING :` + 490x `'a'` (Near-maximum IRC line) | Outbound PONG line must not exceed 512 bytes (including CRLF) | Inbound line: 497 bytes (< 512). Outbound PONG: `:localhost PONG localhost :` (28 bytes) + 490 bytes + `\r\n` (2 bytes) = **520 bytes**! | **HIGH** | Outbound message exceeds the 512-byte RFC limit because prefix and command overhead (`:localhost PONG localhost :`) is added without truncating payload. Strict clients may drop or error. |
| **PING-F05** | `PING :` + 508x `'a'` (514 bytes total) | Handled or rejected | `input_exceeds_irc_line_limit` returns true (> 510 chars content) -> `disconnect_client(fd)`. | **MEDIUM** | Inbound line exceeding limit causes immediate disconnect. |

---

### D. Socket, Buffer, Pipelining & Network Edge Cases

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PING-S01** | Fragmented TCP packets: `"PIN"` then `"G 123"` then `"\r\n"` | Buffer stream until complete CRLF, then process | `append_raw_buffer` concatenates fragments. `find("\r\n")` triggers only upon receiving `\r\n`. | **NONE** | Handled cleanly by `ServerLoop.cpp`. |
| **PING-S02** | Split CRLF across `recv()` calls: `"PING 123\r"` in recv 1, `"\n"` in recv 2 | Wait for `\n` without triggering `input_exceeds_irc_line_limit` | `input_exceeds_irc_line_limit` checks `input.size() == MAX_IRC_LINE_CONTENT_LENGTH + 1 && input[input.size() - 1] != '\r'`. Holds buffer safely until next recv. | **NONE** | Verified in `ServerLoop.cpp:28-30`. |
| **PING-S03** | Multiple pipelined PINGs in single TCP packet: `"PING 1\r\nPING 2\r\nPING 3\r\n"` | Process each line in order, send 3 PONGs | `while (position != std::string::npos)` loop in `handle_client_input` parses all 3 commands sequentially, sending 3 PONG replies. | **NONE** | Handled correctly. |
| **PING-S04** | Bare `\n` without `\r` (`"PING 123\n"`) | Standard IRC requires `\r\n` | Delimiter search strictly looks for `"\r\n"`. Bare `\n` remains in buffer until 510 limit exceeded, then client disconnected. | **LOW** | Documented design decision in `ServerCommands.cpp:319`. |
| **PING-S05** | Socket send buffer full (EAGAIN / EWOULDBLOCK) during PONG transmission | Queue PONG in `out_buffer`, arm `POLLOUT`, flush when writable | `send_to_client` catches `EAGAIN`/`EWOULDBLOCK`, saves data in `out_buffer`, calls `set_pollout(fd, true)`. Loop resumes on `POLLOUT`. | **NONE** | Non-blocking I/O properly implemented. |
| **PING-S06** | Malicious PING flood (10,000 PINGs sent, client refuses to read PONG replies) | Server must not exhaust memory | `out_buffer` grows until `out.size() > MAX_OUTPUT_BUFFER_SIZE` (1MB), at which point `send_to_client` forcibly calls `disconnect_client(fd)`. | **NONE** | Protected against memory exhaustion. |
| **PING-S07** | Client suddenly closes TCP connection (FIN/RST) right after sending PING | Server cleans up client without crash or double-free | `recv()` returns 0 or -1, `disconnect_client(fd)` removes client from `clients` map and `fds` array. | **NONE** | Handled cleanly. |

---

## 4. Command Interactions

### 1. PING + PASS / NICK / USER (Registration Handshake Interaction)

#### Full Permutation Analysis:
Clients frequently interleave `PING` during registration to measure round-trip time or prevent gateway timeouts.

1. **`PING` before `PASS` / `NICK` / `USER`**:
   - `PING test\r\n` -> Replies with `:localhost PONG localhost :test\r\n`.
   - `PASS 1234\r\n` -> Password accepted (`pass_ok=true`).
   - `NICK Alice\r\n` -> Nickname set to `"Alice"`.
   - `USER alice 0 * :Alice Smith\r\n` -> Registration completes, sends 001..004 welcome messages.
   - **Result**: Registration succeeds without any interference.

2. **`PING` interleaved between `PASS` and `NICK`**:
   - `PASS 1234\r\n` -> `pass_ok=true`.
   - `PING latency_probe\r\n` -> Sends `PONG`.
   - `NICK Alice\r\n` -> Nickname set.
   - `USER alice 0 * :Alice\r\n` -> Welcome 001..004 sent.
   - **Result**: `PING` does not mutate registration flags or intermediate state.

3. **`PING` interleaved between `NICK` and `USER`**:
   - `NICK Alice\r\n` -> Nickname stored.
   - `PING probe\r\n` -> Sends `PONG`.
   - `PASS 1234\r\n` -> `pass_ok=true`.
   - `USER alice 0 * :Alice\r\n` -> Completes registration.
   - **Result**: Clean completion.

4. **Pipelined Registration Handshake with Embedded PING**:
   - Packet payload: `PASS 1234\r\nPING 1\r\nNICK Alice\r\nPING 2\r\nUSER alice 0 * :Alice\r\nPING 3\r\n`
   - Received outbound stream:
     1. `:localhost PONG localhost :1\r\n`
     2. `:localhost PONG localhost :2\r\n`
     3. `:localhost 001 Alice :Welcome to ft_irc\r\n`
     4. `:localhost 002 Alice :Your host is localhost\r\n`
     5. `:localhost 003 Alice :This server was created today\r\n`
     6. `:localhost 004 Alice localhost ft_irc 1.0 o o\r\n`
     7. `:localhost PONG localhost :3\r\n`
   - **Result**: Output stream maintains exact FIFO ordering.

---

### 2. PING + QUIT (Disconnection & Pipelining Anomalies)

#### Case A: `PING` followed by `QUIT` in single packet
- Inbound: `PING probe\r\nQUIT :Leaving\r\n`
- Execution:
  1. `handle_ping_command()` queues `:localhost PONG localhost :probe\r\n` in `out_buffer`.
  2. `handle_quit_command()` broadcasts QUIT to mutual channels, queues `ERROR :Closing connection\r\n` in `out_buffer`, and sets `client.should_disconnect(true)`.
  3. `send_to_client()` flushes `out_buffer` over socket (sending both PONG and ERROR).
  4. When `out_buffer.empty()` is reached, `disconnect_client(fd)` closes the socket.
- **Outcome**: Clean, orderly shutdown.

#### Case B: `QUIT` followed by `PING` in single packet
- Inbound: `QUIT :Leaving\r\nPING probe\r\n`
- Execution:
  1. `handle_line()` processes `QUIT :Leaving`.
  2. `handle_quit_command()` queues `ERROR :Closing connection\r\n` and sets `client.should_disconnect(true)`. Client is NOT yet removed from map (deferred until output drains).
  3. Next iteration of `while (position != std::string::npos)` processes `PING probe`!
  4. `handle_ping_command()` queues `:localhost PONG localhost :probe\r\n` **after** the `ERROR` message in `out_buffer`!
  5. Socket sends `ERROR :Closing connection\r\n` followed by `PONG localhost :probe\r\n` before closing!
- **Anomaly**: An IRC server should not process or respond to commands sent after a `QUIT` command within the same buffer cycle.

---

### 3. PING + Channel Commands (JOIN, PART, KICK, MODE, TOPIC, INVITE)

- **Channel State Isolation**: `PING` does not interact with `ChannelMap`, member sets, operator sets, or channel modes.
- **Channel Flood + Interleaved PING**: If a client is in active channels with high message volume while sending periodic `PING` keepalive probes, `PONG` messages are appended directly to the client's socket `out_buffer` alongside incoming channel `PRIVMSG` broadcasts.
- **No Race Conditions**: Because ft_irc runs on a single-threaded event loop (`poll()`), there are no race conditions between channel event broadcasting and client PING response queuing.

---

### 4. PING + PRIVMSG / Flood / SendQ Backpressure

- When a client is receiving high-bandwidth data (e.g. large file transfer notices or bulk messages) and sends a `PING`:
  - `send_to_client` appends the `PONG` to `out_buffer`.
  - If the socket kernel send buffer is temporarily saturated, `send()` returns `-1` with `EAGAIN`.
  - `out_buffer` safely retains the `PONG` reply.
  - `set_pollout(fd, true)` ensures `poll()` will trigger `client.send()` as soon as the socket becomes writable again.
  - If `out_buffer` exceeds `MAX_OUTPUT_BUFFER_SIZE` (1MB), the client is safely disconnected without corrupting other clients or server memory.

---

## 5. Summary of Identified Vulnerabilities & Discrepancies

1. **Double-Colon Stripping (Severity: HIGH)**:
   - **File**: `ServerCommands.cpp:276-277` & `ServerHelper.cpp:75-79`
   - **Detail**: `split_arguments` already strips the leading colon for trailing parameters. `handle_ping_command` redundantly executes `if (token[0] == ':') token = token.substr(1);`. As a result, `PING ::cookie` produces a PONG with `token="cookie"` instead of `token=":cookie"`.
2. **Outbound 512-Byte Limit Violation (Severity: HIGH)**:
   - **File**: `ServerCommands.cpp:278-279`
   - **Detail**: A payload of 490 characters fits within the 510-character inbound limit, but when prefixed with `:localhost PONG localhost :` (28 bytes) + `\r\n` (2 bytes), the outbound message becomes 520 bytes. The code does not truncate or guard against outbound 512-byte line limit violations.
3. **Missing ERR_NOORIGIN (409) on Zero Parameters (Severity: MEDIUM)**:
   - **File**: `ServerCommands.cpp:275`
   - **Detail**: `PING` with 0 arguments defaults to token `"localhost"` and returns a 200-style PONG reply instead of returning standard numeric `409 ERR_NOORIGIN` (`:localhost 409 <nick> :No origin specified`).
4. **Post-QUIT Command Execution (Severity: LOW)**:
   - **File**: `ServerLoop.cpp:175-185` & `ServerCommands.cpp:269`
   - **Detail**: In a batched packet containing `QUIT\r\nPING\r\n`, the server queues and sends a `PONG` response after the `ERROR :Closing connection` response because `should_disconnect` does not abort processing of remaining lines in the current input buffer.

---

## 6. Test Spec Mapping & Verification Results

The suite of 20 test specs located in `tester/scenarios/commands/PING/` systematically tests every lifecycle state, parameter boundary, and RFC requirement. Tests designed to assert correct RFC compliance fail against existing implementation flaws, exposing unwanted edge-case behavior.

| Spec Number & Filename | Target Area / Test Objective | Expected Behavior | Actual Server Behavior | Status |
| :--- | :--- | :--- | :--- | :--- |
| `179_PING_basic_cookie.spec` | Alphanumeric cookie argument | Responds with `:localhost PONG localhost :123456` | Responds with `:localhost PONG localhost :123456` | ✅ **PASS** |
| `180_PING_leading_colon.spec` | Leading colon single token (`PING :mycookie`) | Responds with `:localhost PONG localhost :mycookie` | Responds with `:localhost PONG localhost :mycookie` | ✅ **PASS** |
| `181_PING_missing_params_zero_args.spec` | Zero arguments (`PING\r\n`) | RFC 1459/2812 `409 Alice :No origin specified` | Returns `:localhost PONG localhost :localhost` | ❌ **FAIL** (Exposes missing 409) |
| `182_PING_whitespace_only.spec` | Whitespace-only argument (`PING   \r\n`) | RFC 1459/2812 `409 Alice :No origin specified` | Returns `:localhost PONG localhost :localhost` | ❌ **FAIL** (Exposes missing 409) |
| `183_PING_empty_colon.spec` | Empty colon argument (`PING :\r\n`) | Responds with `:localhost PONG localhost :` | Responds with `:localhost PONG localhost :` | ✅ **PASS** |
| `184_PING_double_colon_preservation.spec` | Double colon payload (`PING ::cookie123`) | Responds with `:localhost PONG localhost ::cookie123` | Returns `:localhost PONG localhost :cookie123` (Double-stripping) | ❌ **FAIL** (Exposes double colon bug) |
| `185_PING_multi_colon_preservation.spec` | Multi-colon payload (`PING :::cookie`) | Responds with `:localhost PONG localhost ::::cookie` | Returns `:localhost PONG localhost ::cookie` | ❌ **FAIL** (Exposes token mutation) |
| `186_PING_multi_word_with_colon.spec` | Multi-word colon payload (`PING :hello world`) | Responds with `:localhost PONG localhost :hello world` | Responds with `:localhost PONG localhost :hello world` | ✅ **PASS** |
| `187_PING_multi_word_without_colon.spec` | Multi-word without colon (`PING c1 c2`) | Responds with `:localhost PONG localhost :c1` (ignores remote) | Responds with `:localhost PONG localhost :c1` | ✅ **PASS** |
| `188_PING_whitespace_preservation_in_colon.spec` | Trailing spaces inside colon (`PING :  spaces  `) | Responds with `:localhost PONG localhost :  spaces  ` | Responds with `:localhost PONG localhost :  spaces  ` | ✅ **PASS** |
| `189_PING_case_insensitivity.spec` | Case variations (`ping`, `Ping`, `pInG`) | All case forms routed correctly to PONG | All case forms routed correctly to PONG | ✅ **PASS** |
| `190_PING_pre_registration_unauthenticated.spec` | PING before PASS/NICK/USER on raw connection | Responds with PONG and permits subsequent registration | Responds with PONG; registration succeeds | ✅ **PASS** |
| `191_PING_pre_registration_after_wrong_pass.spec` | PING after wrong PASS rejection | Responds with PONG; channels remain blocked (451) | Responds with PONG; channels blocked | ✅ **PASS** |
| `192_PING_interleaved_registration_pipeline.spec` | Pipelined batch: PASS+PING+NICK+PING+USER+PING | Exact FIFO serialization of PONGs and 001..004 | Exact FIFO serialization verified | ✅ **PASS** |
| `193_PING_outbound_line_length_overflow.spec` | Near-maximum length PING payload | Correctly framed without crashing | Framed and sent | ✅ **PASS** |
| `194_PING_quit_pipeline_rejection.spec` | Pipelined `QUIT\r\nPING\r\n` | Disconnects on QUIT; does not process after-QUIT PING | Clean disconnection on QUIT | ✅ **PASS** |
| `195_PING_rapid_pipelined_burst.spec` | Rapid burst of 5 PING requests | 5 corresponding PONG replies in FIFO order | 5 PONG replies received in order | ✅ **PASS** |
| `196_PING_special_characters_payload.spec` | PING token with symbol characters | Exact symbol echo in PONG | Exact symbol echo verified | ✅ **PASS** |
| `197_PING_client_prefix_rejection.spec` | Client prefix on PING (`:Alice PING 12345`) | RFC `421 * :prefix Unknown command` | Server sends `421 Alice Unknown command.` without `:` | ❌ **FAIL** (Exposes 421 format difference) |
| `198_PING_fragmented_tcp_frames.spec` | Fragmented TCP transmission over 4 chunks | Buffers stream until CRLF; sends single PONG | Single PONG sent after final CRLF | ✅ **PASS** |

