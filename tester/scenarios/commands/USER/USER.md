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
4. [Malicious Actors & Adversarial Break-the-Code Scenarios](#4-malicious-actors--adversarial-break-the-code-scenarios)
5. [Command Interactions (What Happens When USER Interacts With...)](#5-command-interactions)
   - [1. USER + PASS + NICK (All 6 Registration Permutations & Failure Modes)](#1-user--pass--nick-all-6-registration-permutations--failure-modes)
   - [2. USER + QUIT / Unexpected Disconnect](#2-user--quit--unexpected-disconnect)
   - [3. USER + PRIVMSG / NOTICE / PING / CAP](#3-user--privmsg--notice--ping--cap)
   - [4. USER + JOIN / PART / NAMES](#4-user--join--part--names)
   - [5. USER + MODE / KICK / INVITE / TOPIC](#5-user--mode--kick--invite--topic)
6. [Summary of Identified Vulnerabilities & Recommended Fixes](#6-summary-of-identified-vulnerabilities--recommended-fixes)
7. [Comprehensive Test Spec Mapping (Standard & Adversarial)](#7-comprehensive-test-spec-mapping-standard--adversarial)

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
   - Calls split_arguments(line) -> ["alice", "0", "*", "Alice Wonderland"]
   - Calls dispatch_command(client, "USER", line, arguments)
         │
         ▼
[ ServerCommands.cpp: handle_user_command(client, arguments) ]
   │
   ├─► 1. Check: arguments.empty()?
   │        └─► YES: send_status(client, "461", "USER :Not enough parameters") -> RETURN
   │        (BUG: Should check arguments.size() < 4 per RFC 1459/2812)
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

---

## 3. Deep Edge Case Matrix

### A. Input Parsing & Parameter Count Flaws

| ID | Scenario / Input | Expected RFC Behavior | Current Code Behavior | Severity | Root Cause & Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **USER-P01** | `USER alice` (1 parameter) | `461 USER :Not enough parameters` | Accepted. Sets `username="alice"`. | **HIGH** | `handle_user_command` checks `if (arguments.empty())` instead of `if (arguments.size() < 4)`. |
| **USER-P02** | `USER alice 0` (2 parameters) | `461 USER :Not enough parameters` | Accepted. Sets `username="alice"`. | **HIGH** | Missing 4-parameter check. |
| **USER-P03** | `USER alice 0 *` (3 parameters) | `461 USER :Not enough parameters` | Accepted. Sets `username="alice"`. | **HIGH** | Missing 4-parameter check. |
| **USER-P04** | `USER    alice    0    *    :Real Name` (Extra whitespace) | Clean tokens: `["alice", "0", "*", "Real Name"]` | `split_arguments` skips consecutive spaces properly. | **LOW** | Handled correctly. |
| **USER-P05** | `USER :alice 0 * :Real Name` (Colon on first param) | Parse username as `"alice"` | `split_arguments` treats colon as start of trailing parameter: `arguments[0] = "alice 0 * :Real Name"`. | **CRITICAL** | Embeds spaces in username, corrupting hostmask prefixes across all commands. |
| **USER-P06** | `USER : 0 * :Real` (Single colon username) | Reject with `461` or `432` | Username stored as `" 0 * :Real"` with leading space. | **HIGH** | Malformed hostmask. |
| **USER-P07** | `USER\talice\t0\t*\t:Real` (Tab delimiter) | Reject (only 0x20 spaces valid in IRC BNF) | Command token becomes `"USER\talice..."` -> `421 Unknown command.` | **LOW** | Correctly rejected. |

---

## 4. Malicious Actors & Adversarial Break-the-Code Scenarios

### 1. IRC Line Smuggling / CRLF Injection via Raw `\n` in Username (`USER-ADV01`)
- **Attack Vector**: An attacker connects and sends:
  `USER alice\nNICK hijacked 0 * :Real\r\n`
- **Mechanism**: The server delimits messages strictly on `\r\n`. It reads the whole block as one command, extracting `username = "alice\nNICK"`.
- **Impact**: When the server broadcasts messages for this user (e.g. `:Alice!alice\nNICK@localhost JOIN #chan\r\n`), the embedded raw `\n` splits the IRC stream into two separate lines for every client on the channel, enabling IRC command injection / protocol desynchronization on downstream IRC clients and bouncers.

### 2. Overlength Username DoS / Message Line Overflow (`USER-ADV02`)
- **Attack Vector**: Attacker sends a 400-character username:
  `USER aaaa[x400] 0 * :Real\r\n`
- **Mechanism**: Server lacks a `USERLEN` restriction. Client registers with a 400-byte username.
- **Impact**: When this user speaks in a channel with a long name (`PRIVMSG #long_channel_name :message`), `make_msg` produces a message exceeding `MAX_IRC_LINE_CONTENT_LENGTH` (510 bytes). Other clients on the channel receiving the broadcast may disconnect or crash due to IRC line overflow.

### 3. Client Prefix Spoofing (`USER-ADV03`)
- **Attack Vector**: Attacker attempts to forge server/user prefixes:
  `:spoofed.server.net USER alice 0 * :Alice\r\n`
- **Mechanism**: RFC 2812 §2.3.1 strictly forbids client connections from sending command prefixes.
- **Impact**: Handled cleanly by `is_command` check; returns `421 * Unknown command.`

### 4. Pipelined Post-Registration Username Overwrite (`USER-ADV04`)
- **Attack Vector**: Attacker pipelines multiple commands in one packet:
  `PASS 1234\r\nNICK Alice\r\nUSER legit 0 * :Legit\r\nUSER attacker 0 * :Pwned\r\nJOIN #room\r\n`
- **Mechanism**: First USER completes registration. Second USER is evaluated within the same poll loop.
- **Impact**: Second USER is rejected with `462 :You may not reregister`, preventing post-registration identity tampering.

### 5. Terminal Escape Sequence Injection (`USER-ADV05`)
- **Attack Vector**: Attacker sends ANSI escape sequences in username:
  `USER \x1b[31;1mRoot\x1b[0m 0 * :Real\r\n`
- **Impact**: If accepted without sanitization, recipient terminal clients (irssi, hexchat, weechat) execute the raw escape codes, allowing screen clearing, terminal color hijacking, or cursor repositioning.

---

## 5. Command Interactions

### 1. USER + PASS + NICK (All 6 Registration Permutations)
All 6 permutations (`PASS`->`NICK`->`USER`, `PASS`->`USER`->`NICK`, `NICK`->`PASS`->`USER`, `NICK`->`USER`->`PASS`, `USER`->`PASS`->`NICK`, `USER`->`NICK`->`PASS`) cleanly register the client on the 3rd step with numerics 001–004.

### 2. USER + NICK Collision Race
If an unauthenticated client sends `USER user1`, `PASS 1234`, and collides on `NICK` with an existing user (receiving `433`), the client can supply a new `NICK` and immediately register while preserving the originally buffered `user1` username.

---

## 6. Summary of Identified Vulnerabilities & Recommended Fixes

| Issue ID | Vulnerability | Severity | Recommended Fix |
| :--- | :--- | :--- | :--- |
| **VULN-U01** | **Missing 4-Parameter Count Check** (`arguments.empty()` only) | **HIGH** | Replace `if (arguments.empty())` with `if (arguments.size() < 4)` in `handle_user_command`. |
| **VULN-U02** | **No Username Character Validation** (allows `!`, `@`, control codes, colons, newlines) | **CRITICAL** | Implement `is_valid_username(const Wire &user)` checking alphanumeric characters and reject with `432` if invalid. |
| **VULN-U03** | **No Username Length Limit** (allows 400-char usernames exceeding line buffer) | **HIGH** | Enforce standard `USERLEN` limit (e.g. max 10 or 32 characters). |
| **VULN-U04** | **Colon-Prefixed Parameter Splitting Flaw** (`USER :alice ...`) | **CRITICAL** | In `split_arguments`, only treat `:` as the start of the trailing parameter after expected positional parameters. |

---

## 7. Comprehensive Test Spec Mapping (Standard & Adversarial)

| Spec Number | Spec Filename | Type | Purpose & Expected Behavior |
| :--- | :--- | :--- | :--- |
| **158** | `158_USER_missing_params_zero_args.spec` | RFC Boundary | Tests `USER` with 0 parameters (ERR_NEEDMOREPARAMS 461). |
| **159** | `159_USER_missing_params_one_arg.spec` | RFC Boundary | Tests `USER alice` (1 param, should fail with 461). |
| **160** | `160_USER_missing_params_two_args.spec` | RFC Boundary | Tests `USER alice 0` (2 params, should fail with 461). |
| **161** | `161_USER_missing_params_three_args.spec` | RFC Boundary | Tests `USER alice 0 *` (3 params, should fail with 461). |
| **162** | `162_USER_already_registered_rejection.spec` | RFC State | Tests `USER` issued after registration (ERR_ALREADYREGISTRED 462). |
| **163–168** | `163`–`168_USER_permutation_*.spec` | State Permutations | Tests all 6 arrival permutations of `PASS`, `NICK`, and `USER`. |
| **169** | `169_USER_colon_prefix_username.spec` | Parser Flaw | Tests `USER :alice 0 * :Real` colon handling on username parameter. |
| **170** | `170_USER_whitespace_handling.spec` | Formatting | Tests multiple spaces between USER arguments. |
| **171** | `171_USER_pre_registration_overwrite.spec` | State Machine | Tests sending multiple USER commands before registering. |
| **172** | `172_USER_wrong_password_recovery.spec` | State Recovery | Tests recovery when wrong PASS is sent before/after USER. |
| **173** | `173_USER_unregistered_command_blocking.spec` | Gating | Tests that client who only sent USER cannot execute JOIN or PRIVMSG. |
| **174** | `174_USER_ping_before_registration.spec` | Latency/Ping | Tests that PING works even when only USER is sent. |
| **175** | `175_USER_quit_before_registration.spec` | Disconnect | Tests clean QUIT disconnection when only USER was sent. |
| **176** | `176_USER_prefix_in_privmsg_broadcast.spec` | Propagation | Verifies username is accurately embedded in PRIVMSG prefix. |
| **177** | `177_USER_prefix_in_nick_change_broadcast.spec` | Propagation | Verifies username is preserved in NICK change broadcasts. |
| **178** | `178_USER_invalid_username_characters.spec` | Validation | Tests rejection of `!` and `@` in username. |
| **279** | `279_USER_line_injection_lf_smuggling.spec` | **Adversarial** | Tests raw `\n` line smuggling in USER command. |
| **280** | `280_USER_overlength_dos_broadcast_overflow.spec` | **Adversarial** | Tests 400-char USERLEN overflow causing broadcast overflow. |
| **281** | `281_USER_spoofed_client_prefix_rejection.spec` | **Adversarial** | Tests spoofed server/client prefix rejection on USER. |
| **282** | `282_USER_pipelined_post_registration_exploit.spec` | **Adversarial** | Tests pipelined registration + post-registration exploit command. |
| **283** | `283_USER_empty_colon_username.spec` | **Adversarial** | Tests single colon parameter (`USER : 0 * :Real`). |
| **284** | `284_USER_tab_delimiter_rejection.spec` | **Adversarial** | Tests rejection of TAB delimiters. |
| **285** | `285_USER_nick_collision_race_with_user_state.spec` | **Adversarial** | Tests state preservation during multi-client NICK collision race. |
| **286** | `286_USER_ansi_escape_injection.spec` | **Adversarial** | Tests ANSI escape sequence injection in username. |
| **287** | `287_USER_trailing_parameters_with_internal_colons.spec` | **Edge Case** | Tests multiple internal colons in realname parameter. |
| **288** | `288_USER_multi_word_realname_without_colon.spec` | **Edge Case** | Tests multi-word realname provided without leading colon. |
| **289** | `289_USER_rapid_user_flood_before_pass.spec` | **Stress** | Tests unauthenticated rapid USER command flood before PASS. |
