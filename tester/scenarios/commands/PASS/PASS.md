# Comprehensive PASS Command Flow & Edge Case Analysis

This document provides an exhaustive, line-by-line breakdown of the `PASS` command lifecycle in `ft_irc`. It details input grammar edge cases, state transitions, security vulnerabilities, command interactions, registration gating, password validation mechanics, memory & socket state consistency, and reachable failure modes.

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
                      Server::split_arguments (splits by ' ', extracts prefix/trailing)
                               │
                               ▼
                      Server::dispatch_command
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
     command == "PASS"                     Other Commands
            │                                     │
            ▼                                     ▼
   Server::handle_pass_command          (USER, NICK, CAP, PING, QUIT,
            │                            or 451 ERR_NOTREGISTERED)
            ├───────────────────────────────────────────────┐
            │ arguments.empty()?                            │
            ├──► [Yes] ──► send_status(461, "PASS :Not enough parameters")
            │
            ├───────────────────────────────────────────────┐
            │ client.get_register_status()?                │
            ├──► [Yes] ──► send_status(462, ":You may not reregister")
            │
            ├───────────────────────────────────────────────┐
            │ arguments[0] != get_password()?              │
            ├──► [Yes] ──► client.set_pass_ok(false)        │
            │              send_status(464, ":Password incorrect")
            │
            ▼ [Password Matches]
   client.set_password(arguments[0])
   client.set_pass_ok(true)
   Server::try_register_client(client)
            │
            ▼
   (Checks if nickname, username, and pass_ok are all satisfied;
    if yes, marks client registered and sends 001..004 welcome burst)
```

---

## 2. Line-by-Line Code Analysis & Edge Case Inventory

### A. Input Framing, Tokenization & Delimitation (`ServerCommands.cpp`, `ServerLoop.cpp`)

#### 1. Delimiter Strictness (`\r\n` vs Bare `\n`)
- **Code Reference**: `ServerLoop.cpp:169`, `ServerCommands.cpp:322-332`
- **Implementation**:
  ```cpp
  size_t position = client.get_buffer().find("\r\n");
  ...
  line = client.get_buffer().substr(0, position);
  client.get_buffer().erase(0, position + 2);
  ```
- **Edge Case**: If a client sends `PASS 1234\n` (bare `\n` without `\r`), `find("\r\n")` returns `npos`. The input sits in the buffer until 510 chars are exceeded, at which point `input_exceeds_irc_line_limit()` disconnects the client.
- **RFC Standard**: RFC 1459/2812 §2.3 strictly mandates `\r\n` (CRLF) message framing.

#### 2. Leading Whitespace on Command Token
- **Code Reference**: `ServerCommands.cpp:334`
- **Implementation**:
  ```cpp
  Wire command = line.splitBy(' ')[0].toUpper();
  ```
- **Edge Case**: If a client sends `  PASS 1234\r\n` (leading spaces), `splitBy(' ')[0]` yields an empty string `""`.
- **Result**: `is_command("")` returns `false`, sending `421 Unknown command.` instead of executing `PASS`.

#### 3. Tab Delimiters
- **Code Reference**: `ServerCommands.cpp:334`, `ServerHelper.cpp:65`
- **Implementation**: Tokenizer only splits by `' '` (space), not `\t` (ASCII 0x09).
- **Edge Case**: `PASS\t1234\r\n` extracts command `"PASS\t1234"`, triggering `421 Unknown command.`.
- **Edge Case**: `PASS \t1234\r\n` extracts command `"PASS"`, but `arguments[0]` becomes `"\t1234"`. If server password is `1234`, comparison fails with `464 ERR_PASSWDMISMATCH`.

---

### B. Parameter Validation & Grammar Parsing (`ServerHelper.cpp:62-91`, `ServerCommands.cpp:95-101`)

```cpp
Vector<Wire>	Server::split_arguments(const Wire &line)
{
	Vector<Wire> arguments;
	size_t position = line.find(' ');

	while (position != Wire::npos)
	{
		while (position < line.size() && line[position] == ' ')
			++position;
		if (position >= line.size())
			break;

		size_t next_space = line.find(' ', position);
		if (line[position] == ':')
		{
			arguments.add(line.substr(position + 1));
			break;
		}

		if (next_space == Wire::npos)
		{
			arguments.add(line.substr(position));
			break;
		}
		arguments.add(line.substr(position, next_space - position));
		position = next_space;
	}

	return arguments.ok();
}
```

#### Parsing Matrix for PASS Variations:

| Raw Input | Parsed `arguments` | Code Behavior | Numeric Reply / Status |
| :--- | :--- | :--- | :--- |
| `PASS 1234\r\n` | `["1234"]` | Valid match if server pass is `1234` | Accepted (`pass_ok=true`) |
| `PASS :1234\r\n` | `["1234"]` | Leading colon stripped; valid match | Accepted (`pass_ok=true`) |
| `PASS\r\n` | `[]` (empty) | `arguments.empty()` is true | `461 PASS :Not enough parameters` |
| `PASS    \r\n` | `[]` (empty) | Trailing spaces skipped | `461 PASS :Not enough parameters` |
| `PASS \r\n` | `[]` (empty) | Single trailing space skipped | `461 PASS :Not enough parameters` |
| `PASS :\r\n` | `[""]` (1 empty item) | `arguments.empty()` is false; compares `"" != server_pass` | `464 :Password incorrect` |
| `PASS ::1234\r\n` | `[":1234"]` | First colon stripped, second preserved | `464 :Password incorrect` (unless pass is `:1234`) |
| `PASS :pass word\r\n` | `["pass word"]` | Preserves space inside trailing parameter | Matches if server pass has spaces |
| `PASS pass word\r\n` | `["pass", "word"]` | Checks `arguments[0]` (`"pass"`); ignores `"word"` | Matches if server pass is `"pass"`; fails if pass is `"pass word"` |
| `pass 1234\r\n` | `["1234"]` | Command normalized to `"PASS"` via `.toUpper()` | Accepted (`pass_ok=true`) |
| `Pass 1234\r\n` | `["1234"]` | Command normalized to `"PASS"` via `.toUpper()` | Accepted (`pass_ok=true`) |
| `PASS 1234 5678\r\n` | `["1234", "5678"]` | `arguments[0]` is `"1234"`; extra args ignored | Accepted |

---

### C. Registration & State Transition Edge Cases (`ServerCommands.cpp:95-116`)

```cpp
void	Server::handle_pass_command(Client &client, const Vector<Wire> &arguments)
{
	if (arguments.empty())
	{
		send_status(client, "461", "PASS :Not enough parameters");
		return ;
	}
	if (client.get_register_status())
	{
		send_status(client, "462", ":You may not reregister");
		return ;
	}
	if (arguments[0] != get_password())
	{
		client.set_pass_ok(false);
		send_status(client, "464", ":Password incorrect");
		return ;
	}
	client.set_password(arguments[0]);
	client.set_pass_ok(true);
	try_register_client(client);
}
```

#### 1. State Flipping Mechanics
- **Scenario A: Incorrect Password on Fresh Connection**:
  - `client.set_pass_ok(false)`
  - Sends `464 :Password incorrect`.
  - Connection stays open, allowing client to retry.
- **Scenario B: Correct Password followed by Incorrect Password before Registration**:
  - Step 1: Client sends `PASS correct` $\to$ `pass_ok` becomes `true`.
  - Step 2: Client sends `PASS incorrect` $\to$ `pass_ok` flipped to `false`, server sends `464`.
  - Step 3: Client sends `NICK n` and `USER u 0 * :r`.
  - Result: Client will **NOT** be registered because `pass_ok` was invalidated by Step 2.
- **Scenario C: Incorrect Password followed by Correct Password**:
  - Step 1: Client sends `PASS wrong` $\to$ `pass_ok` is `false`, gets `464`.
  - Step 2: Client sends `PASS correct` $\to$ `pass_ok` becomes `true`.
  - Step 3: Client sends `NICK n` and `USER u 0 * :r`.
  - Result: Client registers successfully.

#### 2. Duplicate `PASS` Post-Registration
- If client has already received `001 RPL_WELCOME` (`client.get_register_status() == true`):
  - Any subsequent `PASS <any_password>` returns `462 :You may not reregister`.
  - `client.pass_ok` is NOT modified.
  - Client remains fully registered.

---

### D. Security & Concurrency Vulnerability: Pre-Auth Nickname Collision via Deferred PASS

#### The "Late PASS" Nick Collision Vulnerability
1. **The Flaw**:
   - In `handle_nick_command` (`ServerCommands.cpp:151-158`):
     ```cpp
     Client &existing_client = get_client(arguments[0]);
     if (existing_client
         && existing_client.get_socket() != client.get_socket()
         && (existing_client.get_register_status() || existing_client.get_pass_ok()))
     {
         send_status(client, "433", arguments[0] + " :Nickname is already in use");
         return ;
     }
     ```
   - In `try_register_client` (`ServerHelper.cpp:95-111`):
     ```cpp
     void Server::try_register_client(Client &client)
     {
         if (client.get_register_status())
             return ;
         if (!client.get_pass_ok())
             return ;
         if (client.get_nickname().empty() || client.get_username().empty())
             return ;

         client.set_register_status(true);
         ...
     }
     ```

2. **Exploitation Timeline**:
   - **T0**: Client 1 connects (Socket 4).
   - **T1**: Client 1 sends `NICK Bob` and `USER bob 0 * :Bob` (Does **not** send `PASS`).
     - Client 1 has `pass_ok == false` and `is_registered == false`. Nickname is stored as `"Bob"`.
   - **T2**: Client 2 connects (Socket 5).
   - **T3**: Client 2 sends `PASS 1234`, `NICK Bob`, `USER bob 0 * :Bob`.
     - When Client 2 sends `NICK Bob`, the server checks `existing_client` (Client 1).
     - Because Client 1 has `get_register_status() == false` AND `get_pass_ok() == false`, the condition `(existing_client.get_register_status() || existing_client.get_pass_ok())` evaluates to **`false`**!
     - Client 2's nickname is set to `"Bob"`, and Client 2 finishes registration as `"Bob"`.
   - **T4**: Client 1 now sends `PASS 1234`.
     - `handle_pass_command` sets `client1.pass_ok = true` and invokes `try_register_client(client1)`.
     - `try_register_client` checks `!client1.get_pass_ok()` (false), `nickname.empty()` (false), `username.empty()` (false).
     - **Bug**: `try_register_client` does **NOT** re-verify whether `"Bob"` is already owned by another registered client (Client 2)!
   - **T5**: **Resulting Catastrophic State**:
     - Both Client 1 (FD 4) and Client 2 (FD 5) are now registered with identical nickname `"Bob"`.
     - `Server::get_client("Bob")` uses `match_nickname` (`Server.cpp:123-131`), which iterates `ClientMap` and returns the first matching client.
     - `PRIVMSG Bob :secret` will only reach one of the clients.
     - `INVITE Bob #chan` will invite whichever client appears first in the map.
     - `KICK #chan Bob` or mode changes will resolve to an arbitrary socket descriptor.

---

## 3. Interaction Matrix: PASS vs Other IRC Commands

| Command | Interacted State / Sequence | Server Behavior | Edge Case / Risk |
| :--- | :--- | :--- | :--- |
| **`NICK`** | `NICK` before `PASS` | Allowed; nickname stored in unauthenticated state. | Nickname collision race if another client takes the nick before PASS is sent (see Vulnerability 2.D). |
| **`USER`** | `USER` before `PASS` | Allowed; username stored in unauthenticated state. | Standard IRC out-of-order registration support. |
| **`PING`** | `PING` before `PASS` | Server replies with `PONG` even before `PASS`. | Allows pre-auth connection latency/liveness check. |
| **`CAP`** | `CAP LS` / `CAP REQ` before/after `PASS` | Server replies with `CAP * LS :` or `CAP * NAK :`. | Negotiates capabilities without requiring password first. |
| **`QUIT`** | `QUIT` before `PASS` | Server sends `ERROR :Closing connection` and closes FD. | Client gracefully aborts before authenticating. |
| **`JOIN`** | `JOIN #chan` before `PASS` | Server rejects with `451 :You have not registered`. | No channel creation or membership leakage. |
| **`PRIVMSG`** | `PRIVMSG target :msg` before `PASS` | Server rejects with `451 :You have not registered`. | No message relay permitted without authentication. |
| **`MODE`** | `MODE target` before `PASS` | Server rejects with `451 :You have not registered`. | No mode queries permitted without authentication. |
| **`TOPIC`** | `TOPIC #chan` before `PASS` | Server rejects with `451 :You have not registered`. | No channel topic information leaked. |
| **`INVITE`** | `INVITE nick #chan` before `PASS` | Server rejects with `451 :You have not registered`. | No invitation actions permitted. |
| **`KICK`** | `KICK #chan nick` before `PASS` | Server rejects with `451 :You have not registered`. | No channel kick actions permitted. |
| **`PART`** | `PART #chan` before `PASS` | Server rejects with `451 :You have not registered`. | No channel part actions permitted. |

---

## 4. Socket, Network, and Memory Lifecycle Edge Cases

### A. Pipelined Packets (Command Aggregation)
- **Scenario**: Client sends all registration commands in a single `send()` syscall:
  `PASS 1234\r\nNICK alice\r\nUSER alice 0 * :Alice\r\n`
- **Execution Flow**:
  1. `handle_client_input` reads entire buffer.
  2. Loop 1: processes `PASS 1234` $\to$ sets `pass_ok = true`.
  3. Loop 2: processes `NICK alice` $\to$ sets nickname.
  4. Loop 3: processes `USER alice` $\to$ sets username $\to$ `try_register_client` triggers $\to$ `001..004` emitted.
- **Verdict**: Correctly handled by line-by-line delimiter extraction loop.

### B. TCP Stream Fragmentation Across PASS Command
- **Scenario**: Client writes fragmented bytes:
  - Packet 1: `PA`
  - Packet 2: `SS 12`
  - Packet 3: `34\r\n`
- **Execution Flow**:
  1. Packet 1: `client.get_buffer()` is `"PA"`. `find("\r\n")` returns `npos`.
  2. Packet 2: `client.get_buffer()` is `"PASS 12"`. `find("\r\n")` returns `npos`.
  3. Packet 3: `client.get_buffer()` is `"PASS 1234\r\n"`. `find("\r\n")` succeeds $\to$ executes `PASS 1234`.
- **Verdict**: Handled correctly by incremental buffering in `Client::append_raw_buffer`.

### C. Socket Disconnection / Reset During Authentication
- **Scenario**: Client connects, sends `PASS 1234`, and drops TCP connection (sends `TCP RST` or closes).
- **Execution Flow**:
  - Next `poll()` cycle detects `POLLHUP` or `recv()` returns 0/error.
  - `disconnect_client(client_fd)` cleanly erases the client from `clients` map and `fds` vector, closing the FD.
- **Verdict**: No memory leaks or lingering half-open state.

### D. File Descriptor Reuse Safety
- **Scenario**: Client on FD 4 disconnects after failed `PASS`. A new client connects and OS reallocates FD 4.
- **Implementation**: `accept_new_client` calls `add_client(client_socket)` which assigns `clients[socket] = Client(socket, this)`.
- **Verdict**: Completely resets `pass_ok`, `is_registered`, `password`, `buffer`, and `out_buffer` to initial clean state.

---

## 5. Summary of Key Findings & Recommendations

1. **Fix Nickname Hijack / Dual-Registration Bug**:
   - In `try_register_client(Client &client)`, before setting `is_registered = true`, perform a collision check:
     ```cpp
     Client &existing = get_client(client.get_nickname());
     if (existing && existing.get_socket() != client.get_socket() && existing.get_register_status()) {
         send_status(client, "433", client.get_nickname() + " :Nickname is already in use");
         client.set_nickname("");
         return;
     }
     ```
2. **Prevent Nickname Reservation by Unauthenticated Clients**:
   - `handle_nick_command` already allows authenticated clients (`pass_ok == true`) to take unauthenticated clients' nicks, but because `try_register_client` lacks the validation check, stale nicknames collide.
3. **Empty Colon Trailing Parameter Handling**:
   - `PASS :` produces an empty string argument instead of empty vector, which evaluates to a password check against `""`. Ensure server startup password cannot be empty (`main.cpp` enforces this).

---

## 6. Test Specification Suite (`tester/scenarios/commands/PASS/`)

The following test specifications systematically verify every nominal flow, edge case, grammar permutation, state transition, and vulnerability:

| Spec File | Target Scenario | Expected Behavior | Edge / Vulnerability Tested |
| :--- | :--- | :--- | :--- |
| `199_PASS_missing_params_zero_args.spec` | `PASS\r\n` (0 args) | `461 * PASS :Not enough parameters` | Parameter validation |
| `200_PASS_whitespace_only.spec` | `PASS    \r\n` | `461 * PASS :Not enough parameters` | Whitespace token stripping |
| `201_PASS_empty_colon.spec` | `PASS :\r\n` | `464 * :Password incorrect` | Empty trailing parameter |
| `202_PASS_double_colon.spec` | `PASS ::1234\r\n` | `464 * :Password incorrect` | Colon stripping preservation |
| `203_PASS_correct_with_colon.spec` | `PASS :1234` | `001 Alice :*` | RFC standard trailing colon |
| `204_PASS_correct_without_colon.spec` | `PASS 1234` | `001 Alice :*` | Standard un-prefixed password |
| `205_PASS_wrong_password.spec` | `PASS wrong` | `464 * :Password incorrect` | Incorrect password rejection |
| `206_PASS_case_sensitivity_password.spec`| `PASS 1234ABCD` | `464 * :Password incorrect` | Case-sensitive password check |
| `207_PASS_case_insensitivity_command.spec` | `pass 1234` | `001 Alice :*` | Lowercase command verb |
| `208_PASS_case_insensitivity_mixed_command.spec` | `PaSs 1234` | `001 Alice :*` | Mixed case command verb |
| `209_PASS_extra_arguments_ignored.spec` | `PASS 1234 extra` | `001 Alice :*` | Trailing extra arguments ignored |
| `210_PASS_password_with_spaces_in_colon.spec` | `PASS :1234 extra` | `464 * :Password incorrect` | Space preservation in colon param |
| `211_PASS_already_registered_rejection.spec` | Duplicate `PASS` | `462 Alice :You may not reregister` | Post-registration protection |
| `212_PASS_already_registered_wrong_pass_rejection.spec` | Wrong `PASS` post-auth | `462 Alice :You may not reregister` | Prevents post-auth de-auth |
| `213_PASS_state_flip_correct_then_wrong.spec` | Good PASS $\to$ Bad PASS | `464` then blocks registration | `pass_ok` flag invalidation |
| `214_PASS_state_flip_wrong_then_correct_recovery.spec` | Bad PASS $\to$ Good PASS | `464` then registers cleanly | Retry recovery support |
| `215_PASS_permutation_nick_user_pass.spec` | NICK $\to$ USER $\to$ PASS | `001 Alice :*` | Late PASS registration |
| `216_PASS_permutation_user_nick_pass.spec` | USER $\to$ NICK $\to$ PASS | `001 Alice :*` | Out-of-order permutation |
| `217_PASS_permutation_pass_user_nick.spec` | PASS $\to$ USER $\to$ NICK | `001 Alice :*` | Out-of-order permutation |
| `218_PASS_pipelined_registration.spec` | Pipelined TCP frame | `001 Alice :*` | Buffer delimiter chunking |
| `219_PASS_tcp_fragmentation.spec` | Fragmented TCP stream | `001 Alice :*` | Partial read reassembly |
| `220_PASS_unregistered_command_blocking.spec` | JOIN/PRIVMSG/MODE pre-auth | `451 * :You have not registered` | State isolation / gating |
| `221_PASS_ping_before_pass_allowed.spec` | PING pre-PASS | `PONG` response | Latency check before auth |
| `222_PASS_quit_before_pass.spec` | QUIT pre-PASS | `ERROR :Closing connection` | Graceful pre-auth exit |
| `223_PASS_nick_collision_race_vulnerability.spec` | Deferred PASS nick steal | `433 * PassBob :Nickname is already in use` | Dual-registration vulnerability probe |
| `224_PASS_tab_delimiter_rejection.spec` | `PASS\t1234` | `421 * Unknown command.` | Tab tokenization rejection |
| `225_PASS_leading_space_rejection.spec` | `  PASS 1234` | `421 * Unknown command.` | Leading whitespace rejection |
| `255_PASS_embedded_null_byte_mismatch.spec` | `PASS 1234\x00extra` | `464 * :Password incorrect` | Binary null byte truncation attempt |
| `256_PASS_overlong_line_overflow_disconnect.spec` | PASS line > 510 bytes | `EXPECT_DISCONNECT` | Buffer overflow / flood protection |
| `257_PASS_pipelined_duplicate_pass_storm.spec` | Flooded `PASS` post-auth in 1 TCP frame | `462 PassStorm :You may not reregister` | Repeated registration bypass attempt |
| `258_PASS_rapid_state_toggle_pipeline.spec` | Toggling PASS valid/invalid in pipeline | `464` and blocked registration `451` | Pass validity flag invalidation |
| `259_PASS_colon_space_preservation.spec` | `PASS : 1234` | `464 * :Password incorrect` | Colon space preservation |
| `260_PASS_unauthenticated_nick_eviction.spec` | Unauthenticated nick squatted | `001 PassVictim :*` | Authenticated client evicts squatter |
| `261_PASS_ghost_fd_pass_ok_isolation.spec` | Recycled FD after authenticated QUIT | `451 * :You have not registered` | FD reuse auth isolation |
| `262_PASS_control_characters_mismatch.spec` | Binary payload `PASS \x01\x02\x03\x04` | `464 * :Password incorrect` | Control char rejection |
| `263_PASS_double_cr_line_delimiters.spec` | `PASS 1234\r\r\n` | `464 * :Password incorrect` | Non-standard delimiter parsing |
| `264_PASS_interleaved_failed_pass_and_restricted_commands.spec` | Brute force PASS + JOIN/MODE/TOPIC | `464` and `451` with 0 state leak | Interleaved probe isolation |
| `265_PASS_spoofed_prefix_rejection.spec` | Spoofed prefix `:attacker PASS 1234` | `421 * Unknown command.` | Command prefix spoofing protection |

