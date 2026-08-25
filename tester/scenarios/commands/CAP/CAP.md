# Comprehensive CAP Command Flow & Edge Case Analysis

This document provides an exhaustive, line-by-line breakdown of the `CAP` (IRCv3 Capability Negotiation) command lifecycle in `ft_irc`. It details input grammar edge cases, state machine transitions, client-server desynchronization, socket/network buffering behaviors, command interactions, and reachable failure modes.

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
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
      command == "CAP"                 other unregistered commands
            │                                   │
            ▼                                   ▼
    Server::handle_cap_command          Check registration status
            │
            ├─► arguments.empty()?
            │     └─► NO-OP (silent drop, no error reply)
            │
            ├─► arguments[0] == "LS"
            │     └─► client.send(":localhost CAP * LS :")
            │
            ├─► arguments[0] == "ls" (lowercase)
            │     └─► NO-OP (case comparison fails! silent drop)
            │
            ├─► arguments[0] == "END"
            │     └─► NO-OP (empty block `{}`)
            │
            ├─► arguments[0] == "REQ"
            │     └─► NO-OP (no ACK or NAK sent -> client hangs)
            │
            └─► Other subcommands (LIST, CLEAR, ACK, NAK, FOOBAR)
                  └─► NO-OP (silent drop, no 410 or 421)
```

---

## 2. Line-by-Line Code Walkthrough

### A. Line Delimitation and Command Parsing
`ServerLoop.cpp:153-189`, `ServerCommands.cpp:327-351`
```cpp
// ServerLoop.cpp:167
size_t position = client.get_buffer().find("\r\n");
...
handle_line(client, position);
```
```cpp
// ServerCommands.cpp:327-351
void Server::handle_line(Client &client, const size_t &position)
{
    Wire line = client.get_buffer().substr(0, position);
    client.get_buffer().erase(0, position + 2);
    if (line.empty())
        return ;

    Wire command = line.splitBy(' ')[0].toUpper();
    if (is_command(command))
    {
        Vector<Wire> arguments = split_arguments(line);
        dispatch_command(client, command, line, arguments);
    }
    else
        send_status(client, "421", "Unknown command.");
}
```
1. `line` is split by space and the first token is converted to uppercase via `toUpper()`. If the client sends `cap LS\r\n`, `command` becomes `"CAP"`.
2. `is_command(command)` in `ServerHelper.cpp:30-36` returns `true` for `"CAP"`.
3. `split_arguments(line)` splits the remainder of `line` after the first space by `' '`, filtering out empty tokens.
4. `dispatch_command` matches `command == "CAP"` at `ServerCommands.cpp:297` and routes directly to `handle_cap_command(client, arguments)`.

### B. Subcommand Dispatch in `handle_cap_command`
`ServerCommands.cpp:218-229`
```cpp
// When the client asks about extra capabilities of the server on connect,
// it gives a response that it doesn't have them.
void	Server::handle_cap_command(Client &client, const Vector<Wire> &arguments)
{
	if (arguments.size() > 0)
	{
		if (arguments[0] == "LS")
		{
			Wire cap_response = ":localhost CAP * LS :";
			client.send(cap_response);
		}
		else if (arguments[0] == "END") {}
	}
}
```

---

## 3. Comprehensive Inventory of Edge Cases & Failure Modes

### Edge Case 1: Case-Sensitivity Flaw on Subcommands (`CAP ls` vs `CAP LS`)
- **Code Location**: `ServerCommands.cpp:222` (`if (arguments[0] == "LS")`)
- **Mechanism**: While `command` (`"CAP"`) is converted to uppercase via `line.splitBy(' ')[0].toUpper()`, the elements of `arguments` are **not** normalized to uppercase.
- **Trigger**: Client sends `CAP ls\r\n`, `cap ls\r\n`, `CAP Ls 302\r\n`, or `CAP end\r\n`.
- **Failure**: `arguments[0]` is `"ls"`. `arguments[0] == "LS"` evaluates to `false`. The server produces no response and drops the command.
- **RFC / IRCv3 Standard**: IRC grammar is strictly case-insensitive for command and subcommand verbs (RFC 2812 §2.1, IRCv3 CAP specification).
- **Impact**: Modern IRC clients transmitting lowercase subcommands will never receive `CAP * LS :`, causing capability negotiation to stall or fallback to legacy registration modes.

---

### Edge Case 2: Unhandled `CAP REQ` Causes Client Handshake Deadlock / Hang
- **Code Location**: `ServerCommands.cpp:220-229`
- **Mechanism**: When a client requests a capability (e.g. `CAP REQ :multi-prefix`, `CAP REQ :sasl`, `CAP REQ :extended-join`), `arguments[0]` is `"REQ"`. The `handle_cap_command` function has branches only for `"LS"` and `"END"`.
- **Trigger**: Any modern IRC client connecting with capabilities configured (WeeChat, HexChat, Irssi, ERC, Colloquy, KiwiIRC).
- **Failure**: The server sends neither `CAP * ACK :...` nor `CAP * NAK :...`.
- **IRCv3 Standard**: IRCv3 Capability Negotiation specification explicitly requires:
  > *"If the server does not support any of the requested capabilities, it MUST respond with a CAP NAK subcommand containing the requested capability list."*
- **Impact**: The client remains blocked waiting on socket read for `ACK` or `NAK` before sending `CAP END` or proceeding with registration. The connection hangs until client-side timeout disconnects it.

---

### Edge Case 3: Premature Registration without Waiting for `CAP END` (Race / SASL Bypass)
- **Code Location**: `ServerHelper.cpp:46-62`, `ServerCommands.cpp:118, 136, 175`
- **Mechanism**:
  ```cpp
  void Server::try_register_client(Client &client) {
      if (client.get_register_status()) return;
      if (!client.get_pass_ok()) return;
      if (client.get_nickname().empty() || client.get_username().empty()) return;
      client.set_register_status(true);
      send_status(client, "001", ":Welcome to ft_irc");
      ...
  }
  ```
- **Trigger**: Client sends standard IRCv3 connection sequence:
  ```
  CAP LS 302
  PASS secret
  NICK alice
  USER alice 0 * :Alice Smith
  CAP REQ :sasl
  AUTHENTICATE PLAIN
  ...
  CAP END
  ```
- **Failure**:
  1. `Server::try_register_client` triggers immediately upon processing `USER` because `pass_ok`, `nickname`, and `username` are all populated.
  2. The server marks `is_registered = true` and sends `001`, `002`, `003`, `004` welcome burst.
  3. Capability negotiation was supposed to hold back registration until `CAP END` was received.
- **Impact**:
  - Unauthenticated registration: If SASL is intended, client is fully registered before authentication completes.
  - State desynchronization: Client receives welcome messages while still in capability negotiation state.

---

### Edge Case 4: Hardcoded Target Asterisk `*` in Post-Registration `CAP LS`
- **Code Location**: `ServerCommands.cpp:224`
  ```cpp
  Wire cap_response = ":localhost CAP * LS :";
  ```
- **Mechanism**: The reply always outputs `*` as the second parameter after `CAP`.
- **Trigger**: An already registered client (e.g. nickname `"alice"`) sends `CAP LS\r\n` during active session to query server capabilities.
- **Failure**: Server responds `:localhost CAP * LS :` instead of `:localhost CAP alice LS :`.
- **IRCv3 Standard**: The target parameter in `CAP` replies must be the client's current nickname if one is assigned/registered, and `*` only if the nickname has not yet been established.
- **Impact**: Strict client implementations discard CAP replies that do not match their assigned nickname if they have already completed registration.

---

### Edge Case 5: Missing Subcommands (`CAP LIST`, `CAP CLEAR`, `CAP ACK`, `CAP NAK`)
- **Code Location**: `ServerCommands.cpp:220-229`
- **Missing Subcommands**:
  - `CAP LIST`: Requests currently active capabilities for the client session.
  - `CAP CLEAR`: Requests disabling all currently active capabilities.
  - `CAP ACK`: Client acknowledgement to server.
  - `CAP NAK`: Client rejection to server.
- **Failure**: All of these subcommands hit the implicit fallthrough and are silently ignored.
- **Impact**: Client receives no feedback, resulting in protocol state desynchronization.

---

### Edge Case 6: Zero-Argument `CAP` Command (Silent Drop vs `ERR_NEEDMOREPARAMS` / `ERR_INVALIDCAPCMD`)
- **Code Location**: `ServerCommands.cpp:220` (`if (arguments.size() > 0)`)
- **Trigger**: Client sends bare `CAP\r\n` with no subcommands or arguments.
- **Failure**: `arguments.empty()` is true. `handle_cap_command` executes nothing and returns.
- **RFC Standard**: RFC 2812 §4.6.1 requires numeric error reply `461 ERR_NEEDMOREPARAMS` (`:localhost 461 * CAP :Not enough parameters`) or IRCv3 `410 ERR_INVALIDCAPCMD`.
- **Impact**: Silent failure gives no error indication to debugging operators or automated test suites.

---

### Edge Case 7: Unknown / Invalid Subcommands Produce No Error
- **Code Location**: `ServerCommands.cpp:220-229`
- **Trigger**: Client sends `CAP FOOBAR\r\n`, `CAP BOGUS\r\n`, or `CAP VERSION\r\n`.
- **Failure**: Function does nothing.
- **Standard**: IRCv3 specifies numeric reply `410 ERR_INVALIDCAPCMD` (`:localhost 410 * FOOBAR :Invalid CAP subcommand`) or RFC 2812 `421 ERR_UNKNOWNCOMMAND`.
- **Impact**: Malformed client requests fail silently without diagnostic feedback.

---

### Edge Case 8: IRCv3.2 Multi-line / Version Argument Ignored (`CAP LS 302`)
- **Code Location**: `ServerCommands.cpp:222-226`
- **Trigger**: Modern clients connecting with IRCv3.2 support send `CAP LS 302`.
- **Analysis**:
  - `arguments[0]` is `"LS"`.
  - `arguments[1]` is `"302"`.
  - Server sends `:localhost CAP * LS :`.
- **Behavior**: Because the server advertises empty capabilities (`:`), sending IRCv3.1 format `:localhost CAP * LS :` is technically accepted by most 3.2 parsers as "no capabilities available". However, if capabilities were added in the future without multi-line `*` flag handling, clients expecting 3.2 format could misparse.

---

### Edge Case 9: Trailing Colon & Multi-Parameter Grammar Edge Cases
- **Trigger A**: `CAP LS :` (trailing colon with empty trailing param).
  - `arguments[0]` = `"LS"`, `arguments[1]` = `":"` (or empty depending on split). `arguments[0] == "LS"` matches.
- **Trigger B**: `CAP   LS   ` (extra spaces).
  - `split_arguments` uses `filter(is_empty)`, so `arguments[0]` is correctly `"LS"`.
- **Trigger C**: `CAP :LS` (colon prefix before subcommand).
  - `arguments[0]` becomes `":LS"`. `arguments[0] == "LS"` evaluates to **false**!
  - Sending `CAP :LS` fails silently.

---

### Edge Case 10: Interaction with Post-Registration Commands & Bypassing `451 ERR_NOTREGISTERED`
- **Code Reference**: `ServerCommands.cpp:290-319`
  ```cpp
  void Server::dispatch_command(...)
  {
      if (command == "PASS")
          handle_pass_command(client, arguments);
      else if (command == "USER")
          handle_user_command(client, arguments);
      else if (command == "NICK")
          handle_nick_command(client, arguments);
      else if (command == "CAP")
          handle_cap_command(client, arguments);
      else if (command == "PING")
          handle_ping_command(client, arguments);
      else if (command == "QUIT")
          handle_quit_command(client, line, arguments);
      else if (!client.get_register_status())
          send_status(client, "451", ":You have not registered");
      ...
  }
  ```
- **Analysis**:
  - `CAP` is dispatched before the `!client.get_register_status()` check.
  - This is **correct** for `CAP`, `PASS`, `NICK`, `USER`, `PING`, and `QUIT` because `CAP` must be permitted prior to registration.
  - Furthermore, `CAP` can be sent after registration without triggering `462 ERR_ALREADYREGISTERED` (unlike `PASS` and `USER` which explicitly reject post-registration calls).

---

### Edge Case 11: CAP Flooding & Outbound Buffer Saturation
- **Code Reference**: `ServerLoop.cpp:113-122`, `ServerCommands.cpp:224-225`
- **Trigger**: Unregistered client connects and sends 10,000 `CAP LS\r\n` pipelined commands in rapid succession.
- **Mechanism**:
  1. Each `CAP LS` queues 25 bytes (`:localhost CAP * LS :\r\n`) into `client.get_out_buffer()`.
  2. If the client does not read from its socket, `out.size()` grows by 250 KB.
  3. If `out.size() > MAX_OUTPUT_BUFFER_SIZE` (1 MB), `Server::send_to_client` executes `disconnect_client(fd)`.
- **Verdict**: The server is protected against memory exhaustion crashes by the 1 MB SendQ limit, cleanly disconnecting the abusive client.

---

## 4. State Transition Matrix & Reachable Undesired States

| Initial State | Command Input | Server Action | Resulting State | Undesired? / Vulnerability |
|---|---|---|---|---|
| Unregistered | `CAP LS\r\n` | Sends `:localhost CAP * LS :\r\n` | Unregistered | No (Expected behavior) |
| Unregistered | `CAP ls\r\n` | Silent drop (no reply) | Unregistered | **Yes** (Case sensitivity bug; client stalls) |
| Unregistered | `CAP REQ :multi-prefix\r\n` | Silent drop (no ACK/NAK) | Unregistered | **Yes** (Client hangs waiting for ACK/NAK) |
| Unregistered | `CAP FOOBAR\r\n` | Silent drop (no error) | Unregistered | **Yes** (Missing 410 `ERR_INVALIDCAPCMD`) |
| Unregistered | `CAP\r\n` | Silent drop (no error) | Unregistered | **Yes** (Missing 461 `ERR_NEEDMOREPARAMS`) |
| Unregistered (CAP initiated) | `PASS` -> `NICK` -> `USER` | Sends `001-004` immediately | **Registered** | **Yes** (Bypasses `CAP END` hold; SASL race) |
| Registered (`alice`) | `CAP LS\r\n` | Sends `:localhost CAP * LS :\r\n` | Registered (`alice`) | **Minor** (Target should be `alice`, not `*`) |
| Unregistered | `CAP :LS\r\n` | Silent drop (`:LS` != `LS`) | Unregistered | **Yes** (Colon prefix in param fails) |
| Any | 50,000 x `CAP LS\r\n` (no recv) | SendQ exceeds 1 MB -> closes socket | Disconnected | No (Properly defended against OOM) |

---

## 5. Concrete Reproduction Scenarios

### Scenario A: Case-Sensitivity Breakdown
```
Client: cap ls\r\n
Server: (crickets... 0 bytes returned)
Client: (hangs or fails connection handshake)
```

### Scenario B: Modern IRC Client Negotiation Deadlock (`CAP REQ`)
```
Client -> Server: CAP LS 302\r\n
Server -> Client: :localhost CAP * LS :\r\n
Client -> Server: CAP REQ :multi-prefix\r\n
Server -> Client: (nothing sent! Should be: :localhost CAP * NAK :multi-prefix\r\n)
Client: (waiting indefinitely for ACK or NAK... times out after 60s)
```

### Scenario C: Colon Prefixed Subcommand Rejection
```
Client -> Server: CAP :LS\r\n
Server: (evaluates arguments[0] == ":LS" != "LS", drops message silently)
```

---

## 6. Recommended Implementation Hardening

To make the `CAP` implementation 100% robust and compliant with IRCv3 / RFC specifications:

1. **Normalize Subcommand to Uppercase & Strip Leading Colon**:
   ```cpp
   Wire subcmd = arguments[0];
   if (!subcmd.empty() && subcmd[0] == ':')
       subcmd = subcmd.substr(1);
   subcmd = subcmd.toUpper();
   ```

2. **Handle All IRCv3 Subcommands & Return NAK / Errors**:
   ```cpp
   if (arguments.empty()) {
       send_status(client, "461", "CAP :Not enough parameters");
       return;
   }
   if (subcmd == "LS") {
       Wire target = client.get_nickname().empty() ? "*" : client.get_nickname();
       client.send(":localhost CAP " + target + " LS :");
   } else if (subcmd == "REQ") {
       // Since server supports no extensions, NAK whatever was requested:
       Wire requested = line.contains(" :") ? line.strAfter(" :") : (arguments.size() > 1 ? arguments[1] : "");
       Wire target = client.get_nickname().empty() ? "*" : client.get_nickname();
       client.send(":localhost CAP " + target + " NAK :" + requested);
   } else if (subcmd == "LIST") {
       Wire target = client.get_nickname().empty() ? "*" : client.get_nickname();
       client.send(":localhost CAP " + target + " LIST :");
   } else if (subcmd == "CLEAR" || subcmd == "END") {
       // Acknowledge or finish CAP negotiation
   } else {
       send_status(client, "410", subcmd + " :Invalid CAP subcommand");
   }
   ```

3. **Dynamic Target Nickname**:
   Always use `client.get_nickname().placeholder("*")` instead of hardcoding `*`.

---

## 7. Test Suite Mapping & Specification Coverage

| Spec File | Test Focus | Expected (Compliant) Behavior | Current Server Failure |
|---|---|---|---|
| [`11_CAP_case_insensitivity.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/11_CAP_case_insensitivity.spec) | `CAP ls` in lowercase | Server sends `:localhost CAP * LS :` | Case-sensitive check fails; silent drop |
| [`12_CAP_req_nak_response.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/12_CAP_req_nak_response.spec) | Single capability `CAP REQ :multi-prefix` | Server replies with `CAP * NAK :multi-prefix` | Drops `CAP REQ` silently; client hangs |
| [`13_CAP_hold_registration_until_end.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/13_CAP_hold_registration_until_end.spec) | Registration hold until `CAP END` | Registration `001` delayed until `CAP END` | Premature welcome burst immediately on `USER` |
| [`14_CAP_registered_client_nick_target.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/14_CAP_registered_client_nick_target.spec) | Post-registration `CAP LS` | Server sends `:localhost CAP Alice LS :` | Hardcoded `*` target (`:localhost CAP * LS :`) |
| [`15_CAP_missing_subcommand_error.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/15_CAP_missing_subcommand_error.spec) | Bare `CAP` (0 parameters) | Server sends `461 * CAP :Not enough parameters` | Silent drop; 0 bytes sent |
| [`16_CAP_invalid_subcommand_error.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/16_CAP_invalid_subcommand_error.spec) | Unknown `CAP BOGUS` | Server sends `410 * :Invalid CAP subcommand` | Silent drop; 0 bytes sent |
| [`17_CAP_colon_prefix_subcommand.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/17_CAP_colon_prefix_subcommand.spec) | Subcommand with colon `CAP :LS` | Server strips colon and replies with `CAP * LS :` | Literal `":LS"` comparison fails; drops silently |
| [`18_CAP_list_subcommand.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/18_CAP_list_subcommand.spec) | Subcommand `CAP LIST` | Server replies with `:localhost CAP * LIST :` | Unhandled subcommand; drops silently |
| [`19_CAP_clear_subcommand.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/19_CAP_clear_subcommand.spec) | Subcommand `CAP CLEAR` | Server acknowledges with `CAP * ACK :` | Unhandled subcommand; drops silently |
| [`20_CAP_end_case_insensitivity.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/20_CAP_end_case_insensitivity.spec) | Subcommand `CAP end` (lowercase) | Server recognizes `end` and finishes CAP phase | Case-sensitive check fails on `"end"` |
| [`21_CAP_req_multiple_nak.spec`](file:///home/tbatis/core/berg/tester/scenarios/commands/CAP/21_CAP_req_multiple_nak.spec) | Multiple capabilities `CAP REQ :foo bar baz` | Server sends `CAP * NAK :foo bar baz` | Drops `CAP REQ` silently; client hangs |

