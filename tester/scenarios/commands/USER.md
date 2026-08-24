# Detailed USER Command Analysis: Lifecycle, Edge Cases & Interactions

A comprehensive, line-by-line audit of the `USER` command implementation in `ft_irc` across the entire codebase (`ServerCommands.cpp`, `ServerHelper.cpp`, `Server.cpp`, `ServerMessaging.cpp`, `ServerLoop.cpp`, `Client.cpp`, `Channel.cpp`, and `Wire.hpp`).

---

## Table of Contents
1. [End-to-End Flow Diagram](#1-end-to-end-flow-diagram)
2. [Code Trace & State Transitions](#2-code-trace--state-transitions)
3. [Deep Edge Case Matrix](#3-deep-edge-case-matrix)
   - [A. Input Parsing & Parameter Count Flaws](#a-input-parsing--parameter-count-flaws)
   - [B. Username Character Validation & Injection Risks](#b-username-character-validation--injection-risks)
   - [C. State Machine & Registration Lifecycle Edge Cases](#c-state-machine--registration-lifecycle-edge-cases)
   - [D. Prefix Generation & User Identity Propagation](#d-prefix-generation--user-identity-propagation)
   - [E. Socket, Buffer & Pipelining Edge Cases](#e-socket-buffer--pipelining-edge-cases)
4. [Command Interactions (What Happens When USER Interacts With...)](#4-command-interactions)
   - [1. USER + PASS + NICK (All 6 Registration Permutations & Failure Modes)](#1-user--pass--nick-all-6-registration-permutations--failure-modes)
   - [2. USER + QUIT / Unexpected Disconnect](#2-user--quit--unexpected-disconnect)
   - [3. USER + PRIVMSG / NOTICE / PING / CAP](#3-user--privmsg--notice--ping--cap)
   - [4. USER + JOIN / PART / NAMES](#4-user--join--part--names)
   - [5. USER + MODE / KICK / INVITE / TOPIC](#5-user--mode--kick--invite--topic)
5. [Summary of Identified Vulnerabilities & Recommended Fixes](#5-summary-of-identified-vulnerabilities--recommended-fixes)

---

## 1. End-to-End Flow Diagram

```
[ TCP Inbound Packet: "USER alice 0 * :Alice Wonderland\r\n" ]
         │
         ▼
[ ServerLoop.cpp: handle_client_input(fd) ]
   - recv() reads into client's raw buffer
   - Checks input_exceeds_irc_line_limit (<= 510 chars before \r\n)
         │
         ▼
[ ServerCommands.cpp: handle_line(client, pos) ]
   - Extracts substring [0, pos], erases [0, pos+2] from client buffer
   - Extracts command: line.splitBy(' ')[0].toUpper() -> "USER"
   - Validates is_command("USER") == true
   - Calls split_arguments(line) -> ["alice", "0", "*", ":Alice", "Wonderland"]
   - Calls dispatch_command(client, "USER", line, arguments)
         │
         ▼
[ ServerCommands.cpp: handle_user_command(client, arguments) ]
   │
   ├─► 1. Check: arguments.empty()?
   │        └─► YES: send_status(client, "461", "USER :Not enough parameters") -> RETURN
   │
   ├─► 2. Check: client.get_register_status() == true?
   │        └─► YES: send_status(client, "462", ":You may not reregister") -> RETURN
   │
   ├─► 3. client.set_username(arguments[0])
   │        └─► Stores arguments[0] directly into client.username (no validation, no length limit)
   │
   └─► 4. try_register_client(client)
            └─► Evaluates:
                - client.get_register_status() == false
                - client.get_pass_ok() == true
                - !client.get_nickname().empty()
                - !client.get_username().empty()
            └─► If all 4 conditions are met:
                     - client.set_register_status(true)
                     - Sends RPL_WELCOME (001): ":localhost 001 <nick> :Welcome to ft_irc"
                     - Sends RPL_YOURHOST (002): ":localhost 002 <nick> :Your host is localhost"
                     - Sends RPL_CREATED (003):  ":localhost 003 <nick> :This server was created today"
                     - Sends RPL_MYINFO (004):   ":localhost 004 <nick> localhost ft_irc 1.0 o o"
```

---

## 2. Code Trace & State Transitions

### State Variables Involved:
- `Client::username` (`Wire`): current username string (default `""`).
- `Client::nickname` (`Wire`): current nickname string (default `""`).
- `Client::password` (`Wire`): client-supplied password string.
- `Client::pass_ok` (`bool`): whether correct PASS was accepted (default `false`).
- `Client::is_registered` (`bool`): whether client completed registration handshake (default `false`).
- `Server::clients` (`Map<int, Client>`): active client sessions mapped by socket FD.

### State Transitions Table for USER:

| Initial Client State | USER Command Line | New Client State | Numeric Reply / Outbound Message |
| :--- | :--- | :--- | :--- |
| `unregistered`, `pass_ok=false`, `nick=""`, `user=""` | `USER alice 0 * :Alice Smith` | `user="alice"`, `unregistered` | *(None - waiting for PASS & NICK)* |
| `unregistered`, `pass_ok=true`, `nick=""`, `user=""` | `USER alice 0 * :Alice Smith` | `user="alice"`, `unregistered` | *(None - waiting for NICK)* |
| `unregistered`, `pass_ok=false`, `nick="ali"`, `user=""` | `USER alice 0 * :Alice Smith` | `user="alice"`, `unregistered` | *(None - waiting for PASS)* |
| `unregistered`, `pass_ok=true`, `nick="ali"`, `user=""` | `USER alice 0 * :Alice Smith` | `user="alice"`, **`REGISTERED`** | **001, 002, 003, 004 (RPL_WELCOME)** |
| `REGISTERED` (`is_registered=true`) | `USER bob 0 * :Bob` | No change | `462 :You may not reregister` |
| Any state | `USER` *(0 arguments)* | No change | `461 USER :Not enough parameters` |
| `unregistered` | `USER alice` *(1 argument)* | `user="alice"`, `unregistered` | *(Accepted! Bug: RFC requires 4 params)* |
| `unregistered` | `USER alice 0` *(2 arguments)* | `user="alice"`, `unregistered` | *(Accepted! Bug: RFC requires 4 params)* |
| `unregistered` | `USER alice 0 *` *(3 arguments)* | `user="alice"`, `unregistered` | *(Accepted! Bug: RFC requires 4 params)* |
| `unregistered` | `USER :alice 0 * :Real` | `user=":alice"`, `unregistered` | *(Accepted with colon prefix!)* |
| `unregistered` | `USER alice!root@hack 0 * :Real`| `user="alice!root@hack"`, `unregistered`| *(Accepted! Spoofs prefix format)* |

---

## 3. Deep Edge Case Matrix

### A. Input Parsing & Parameter Count Flaws

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **USER-P01** | `USER alice` (1 parameter) | `461 USER :Not enough parameters` (RFC 1459 §4.1.3 & RFC 2812 §3.1.3 mandate 4 parameters) | Accepted. Sets `username="alice"`. | **HIGH** | `handle_user_command` checks `if (arguments.empty())` instead of `if (arguments.size() < 4)`. |
| **USER-P02** | `USER alice 0` (2 parameters) | `461 USER :Not enough parameters` | Accepted. Sets `username="alice"`. | **HIGH** | Same as above. Non-standard input accepted without validation. |
| **USER-P03** | `USER alice 0 *` (3 parameters) | `461 USER :Not enough parameters` | Accepted. Sets `username="alice"`. | **HIGH** | Missing 4-parameter check. |
| **USER-P04** | `USER    alice    0    *    :Real Name` (Extra whitespace between tokens) | Tokens parsed cleanly: `["alice", "0", "*", ":Real", "Name"]` | `split_arguments` uses `splitBy(' ').filter(is_empty)` which cleans out consecutive spaces. `username="alice"`. | **LOW** | Handled correctly by `Wire::splitBy` + `filter`. |
| **USER-P05** | `USER :alice 0 * :Real Name` (First argument begins with colon) | Strip leading `:` or parse as `"alice"` | `arguments[0]` becomes `":alice"`. Username is stored with a leading colon. | **MEDIUM** | `split_arguments` does not strip leading colons on regular parameters. |
| **USER-P06** | `USER ""` or `USER   \r\n` (Empty string or whitespace-only) | `461 USER :Not enough parameters` | `arguments.empty()` evaluates to true -> returns `461`. | **LOW** | Handled correctly. |
| **USER-P07** | `user alice 0 * :Real` / `User alice 0 * :Real` (Mixed case command) | Parsed identically to uppercase `USER` | `command = line.splitBy(' ')[0].toUpper()` converts `"user"` to `"USER"`. | **LOW** | Handled correctly. |
| **USER-P08** | ` USER alice 0 * :Real` (Leading whitespace before command) | Ignore leading spaces or reject | `line.splitBy(' ')[0]` returns `""`, `is_command("")` is false -> `421 Unknown command.` | **LOW** | Complies with strict IRC BNF where commands start at column 0. |

---

### B. Username Character Validation & Injection Risks

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **USER-V01** | `USER admin!root@evil.com 0 * :Real` (Username contains `!` or `@`) | Reject with `432 Erroneous nickname` or sanitize characters | Stored verbatim: `username="admin!root@evil.com"`. | **CRITICAL** | When `make_msg` builds `:nick!user@localhost`, it produces `:nick!admin!root@evil.com@localhost`. Downstream IRC clients (irssi, WeeChat, HexChat) will fail to parse the hostmask or misidentify the sender host/user. |
| **USER-V02** | `USER \x1b[31mHacker\x1b[0m 0 * :Real` (ANSI escape sequences in username) | Strip control characters or reject | Stored verbatim with escape codes. | **HIGH** | Broadcast messages like `:nick!\x1b[31mHacker\x1b[0m@localhost PRIVMSG #chan :hi` inject raw terminal escape codes into all recipient terminal emulators. |
| **USER-V03** | `USER "user with space" 0 * :Real` | Split into distinct tokens | `splitBy(' ')` splits on space; `username` becomes `"\"user"`. | **LOW** | No quote-aware parser in `split_arguments`. |
| **USER-V04** | `USER ` + 500x `'a'` + ` 0 * :Real` (500-char username) | Truncate username to `USERLEN` (typically 9, 10, or 32 chars) | Accepts all 500 chars as `username`. | **HIGH** | When client sends `PRIVMSG #chan :msg`, `make_msg` builds a line exceeding the 512-byte IRC message limit. The receiving client/socket might truncate or drop the message. |
| **USER-V05** | `USER null\0byte 0 * :Real` (Null byte injection) | Disconnect or truncate | `recv()` terminates string at `\0` or `Wire` constructor stops at null byte. | **MEDIUM** | Incomplete username stored if internal null bytes exist. |
| **USER-V06** | `USER : 0 * :Real` (Username is single colon) | Reject invalid username | Username is stored as `":"`. | **MEDIUM** | Creates invalid mask `:nick!:!@localhost`. |

---

### C. State Machine & Registration Lifecycle Edge Cases

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **USER-S01** | Multiple `USER` calls before registration (e.g. `USER alice` then `USER bob`) | Overwrite or reject with 462 depending on daemon spec | Overwrites `username` to `"bob"`. No error is sent since `is_registered == false`. | **LOW** | Permitted before registration finishes. |
| **USER-S02** | `USER` sent *after* registration is complete | `462 :You may not reregister` (ERR_ALREADYREGISTRED) | `if (client.get_register_status())` checks and sends `462`. | **LOW** | Complies with RFC 2812 §3.1.3. |
| **USER-S03** | `USER` sent without prior `PASS` | Allowed to buffer `username`, but registration blocked until valid `PASS` | `try_register_client` checks `client.get_pass_ok() == false` and does not register. | **LOW** | Working as designed. |
| **USER-S04** | `USER` sent after wrong `PASS` | `username` is saved, but registration blocked | `client.set_pass_ok(false)` prevents registration. If client subsequently sends correct `PASS`, registration completes immediately. | **LOW** | Working as designed. |
| **USER-S05** | `USER` sent with empty server password | If server requires no password, `PASS` must still be evaluated | `pass_ok` starts `false`, so client must send `PASS ""` to register even if password is empty string. | **MEDIUM** | Inherent behavior of boolean flag `pass_ok`. |
| **USER-S06** | Realname storage & retrieval | RFC 1459/2812 stores 4th param as realname | `Client` class does not have a `realname` field. Realname is completely ignored and discarded. | **LOW** | Acceptable if WHO/WHOIS commands are not part of scope. |

---

### D. Prefix Generation & User Identity Propagation

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **USER-X01** | `make_msg` prefix construction | `:nick!user@localhost <CMD> <target> :<param>` | Constructs string using `client.get_nickname()` and `client.get_username()`. | **MEDIUM** | If `username` contains colons, spaces, `!`, or `@`, generated messages violate RFC prefix grammar. |
| **USER-X02** | Unregistered client sending `QUIT` before `USER` | Disconnect without broadcast or send `ERROR` | `get_client_audience(fd)` is empty for unregistered clients; `make_msg` called with empty `username`, but no channel broadcast occurs. ERROR sent directly. | **LOW** | Safe: no corrupted broadcasts reach other clients. |
| **USER-X03** | Status numeric before `USER` (e.g. `USER` with 0 args) | Send `:localhost 461 * USER :Not enough parameters` | `send_status` uses `client.get_nickname().placeholder("*")`, generating valid `*` fallback for unregistered client. | **LOW** | Fully compliant with RFC 2812. |

---

### E. Socket, Buffer & Pipelining Edge Cases

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **USER-B01** | Fragmented TCP packets: `US` -> `ER al` -> `ice 0 * :Real\r\n` | Reassemble complete command and execute | `Client::append_raw_buffer` buffers until `\r\n` is found. Handled properly. | **LOW** | Robust buffering in `ServerLoop.cpp`. |
| **USER-B02** | Pipelined batch: `PASS 123\r\nNICK alice\r\nUSER alice 0 * :Real\r\n` | Execute commands sequentially in one poll cycle | `while (position != std::string::npos)` processes PASS, NICK, and USER in sequence. Welcome replies (001-004) sent at end of USER. | **LOW** | Correctly registers client in a single recv() cycle. |
| **USER-B03** | Pipelined batch with mid-batch NICK collision: `PASS 123\r\nNICK taken_nick\r\nUSER alice 0 * :Real\r\n` | Reject NICK (433), execute USER, remain unregistered | NICK returns 433, USER sets username to `"alice"`. `try_register_client` does not register because `nickname.empty()` is true. Client remains connected. | **LOW** | Handled correctly. Client can recover by sending a valid `NICK`. |
| **USER-B04** | Line length > 510 characters before `\r\n` | Disconnect client (SendQ/Receive limit) | `input_exceeds_irc_line_limit` returns true -> triggers `disconnect_client(client_fd)`. | **LOW** | Server protected against buffer overflow / unbounded memory growth. |

---

## 4. Command Interactions

### 1. USER + PASS + NICK (All 6 Registration Permutations & Failure Modes)

A client must provide `PASS`, `NICK`, and `USER` to register. Below is the state matrix for all 6 possible arrival sequences:

| Permutation | Sequence Order | Behavior & Verification | Result |
| :--- | :--- | :--- | :--- |
| **Permutation 1** | `PASS` ➔ `NICK` ➔ `USER` | 1. `PASS`: `pass_ok=true`<br>2. `NICK`: `nickname="alice"`<br>3. `USER`: `username="alice"` ➔ `try_register_client` triggers. | **REGISTERED** (Standard IRC client flow) |
| **Permutation 2** | `PASS` ➔ `USER` ➔ `NICK` | 1. `PASS`: `pass_ok=true`<br>2. `USER`: `username="alice"`<br>3. `NICK`: `nickname="alice"` ➔ `try_register_client` triggers. | **REGISTERED** (Alternative standard flow) |
| **Permutation 3** | `NICK` ➔ `PASS` ➔ `USER` | 1. `NICK`: `nickname="alice"`<br>2. `PASS`: `pass_ok=true`<br>3. `USER`: `username="alice"` ➔ `try_register_client` triggers. | **REGISTERED** |
| **Permutation 4** | `NICK` ➔ `USER` ➔ `PASS` | 1. `NICK`: `nickname="alice"`<br>2. `USER`: `username="alice"`<br>3. `PASS`: `pass_ok=true` ➔ `try_register_client` triggers. | **REGISTERED** |
| **Permutation 5** | `USER` ➔ `PASS` ➔ `NICK` | 1. `USER`: `username="alice"`<br>2. `PASS`: `pass_ok=true`<br>3. `NICK`: `nickname="alice"` ➔ `try_register_client` triggers. | **REGISTERED** |
| **Permutation 6** | `USER` ➔ `NICK` ➔ `PASS` | 1. `USER`: `username="alice"`<br>2. `NICK`: `nickname="alice"`<br>3. `PASS`: `pass_ok=true` ➔ `try_register_client` triggers. | **REGISTERED** |

#### Failure Scenarios during Permutations:
- **Wrong Password**: If `PASS` is wrong at step 1, `pass_ok` is `false`. Steps 2 & 3 record `nickname` and `username`, but `try_register_client` will not fire. The client can send `PASS <correct>` at step 4 to complete registration.
- **Nickname Collision**: If `NICK` is taken (433), `nickname` remains `""`. Subsequent `USER` command sets `username`, but registration will not complete until a unique `NICK` is provided.

---

### 2. USER + QUIT / Unexpected Disconnect

- **Scenario**: Unregistered client sends `USER alice 0 * :Alice`, then sends `QUIT :Goodbye`.
- **Trace**:
  1. `handle_quit_command` is invoked.
  2. `get_client_audience(fd)` returns an empty Set (client has no channels).
  3. `client.should_disconnect(true)` is flagged.
  4. `client.send("ERROR :Closing connection")` queues the close error.
  5. As soon as out-buffer drains, `disconnect_client(fd)` closes the socket and purges the client.
- **Scenario**: Socket abruptly closes (TCP FIN/RST) after `USER`.
  1. `recv()` returns 0 or -1.
  2. `disconnect_client(client_fd)` immediately removes the client from `clients` map and `fds` vector.

---

### 3. USER + PRIVMSG / NOTICE / PING / CAP

- **`USER` + `PRIVMSG` / `NOTICE` (Unregistered)**:
  - If client sends `USER alice 0 * :Real` followed by `PRIVMSG #channel :hello` before `NICK` or `PASS`:
  - `dispatch_command` hits `else if (!client.get_register_status())` ➔ sends `451 :You have not registered`.
- **`USER` + `PING` (Unregistered)**:
  - `PING` is dispatched before the registration check in `dispatch_command`.
  - Server replies `:localhost PONG localhost :token`. This allows clients to test latency before completing registration handshake.
- **`USER` + `CAP LS` (Unregistered)**:
  - Handled before registration check. Server replies `:localhost CAP * LS :`. Complies with IRCv3 capability negotiation.

---

### 4. USER + JOIN / PART / NAMES

- An unregistered client who has only sent `USER` cannot execute `JOIN`, `PART`, or query `NAMES`.
- Attempting `JOIN #channel` yields `451 :You have not registered`.
- Once `PASS` and `NICK` are completed, subsequent `JOIN #channel` broadcasts `:nick!user@localhost JOIN #channel` to channel members, embedding the `username` captured during `USER`.

---

### 5. USER + MODE / KICK / INVITE / TOPIC

- All channel administrative commands require `client.get_register_status() == true`.
- If an unregistered client sends `MODE`, `KICK`, `INVITE`, or `TOPIC`, the server immediately responds with `451 :You have not registered`.
- When executed by a registered client, any broadcast generated by these commands includes the user mask `:nick!user@localhost`.

---

## 5. Summary of Identified Vulnerabilities & Recommended Fixes

| Issue ID | Vulnerability | Severity | Recommended Fix |
| :--- | :--- | :--- | :--- |
| **VULN-U01** | **Missing 4-Parameter Count Check** (`arguments.empty()` only) | **HIGH** | Replace `if (arguments.empty())` with `if (arguments.size() < 4)` in `handle_user_command`. |
| **VULN-U02** | **No Username Character Validation** (allows `!`, `@`, control codes, colons) | **CRITICAL** | Implement `is_valid_username(const Wire &user)` checking `user.hasOnlyAlphaNum("-_[]\\`^{}")` and reject with `432` if invalid. |
| **VULN-U03** | **No Username Length Limit** (allows 500-char usernames exceeding line buffer) | **HIGH** | Enforce standard `USERLEN` limit (e.g. `if (arguments[0].length() > 10)` or truncate to 10 characters). |
| **VULN-U04** | **Leading Colon Not Stripped on Username Parameter** (`USER :alice ...`) | **MEDIUM** | Check `if (!arguments[0].empty() && arguments[0][0] == ':') arguments[0] = arguments[0].substr(1);`. |
| **VULN-U05** | **Realname Is Not Stored** (discards 4th parameter `:Real Name`) | **LOW** | Add `Wire realname` field to `Client` class if `WHOIS`/`WHO` support is added in future extensions. |
