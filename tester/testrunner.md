# Developer Specification: IRC Integration & Pen-Test Script Engine

---

## 1. Overview & Purpose
This tool is a scriptable multi-client integration test engine and security fuzzer for IRC server implementations (`ft_irc`).
It manages multiple virtual TCP client connections within a single process to execute scenario scripts, assert IRC protocol behavior, test edge cases (fragmentation/buffering), and log all traffic and failures.

---

## 2. Architecture & Execution Model

* **Single Test Runner**: Manages an arbitrary number of virtual TCP client sockets (`C1`, `C2`, ...).
* **Linear Execution**: Processes script instructions top-to-bottom.
* **Explicit Assertions (`EXPECT`)**: All expected server replies (numeric replies, error codes, command confirmations) are asserted explicitly using `EXPECT`. `SEND` commands send raw IRC commands to the server without any implicit awaiting of responses.
* **Cross-Client Notifications (`WAIT_RECV`)**: Used when a client needs to wait for an **asynchronous broadcast** triggered by another client (e.g., `C2` waiting for `C1`'s `PRIVMSG`, `JOIN`, `KICK`, or `INVITE`).
* **Single Log File per Spec**: All client activity (`C1`, `C2`, etc.) and system events for `test_name.spec` are written to `tester/logs/test_name.log` in chronological order.
* **Failure Handling**: On any assertion failure (`EXPECT`, `WAIT_RECV`, timeout, socket drop), the runner logs the failure to `tester/logs/test_name.log`, prints an error summary to stdout, cleans up sockets, and exits with code `1`.

---

## 3. Script Syntax & Directives

### 3.1 Header
```text
CLIENTS C1, C2, ...
```
Declares all virtual client identifiers used in the test file.

### 3.2 Directives Table

| Directive | Syntax Example | Description |
| :--- | :--- | :--- |
| `SEND` | `C1 SEND JOIN #42` | Sends raw string to server (`\r\n` appended). Does not wait for a response; pair with `EXPECT` if a response is expected. |
| `EXPECT` | `C2 EXPECT 475 Bob #42 :*` | Asserts that the specified client receives a message matching the glob pattern. |
| `WAIT_RECV` | `C2 WAIT_RECV :Alice!* PRIVMSG #42 :Hello` | Blocks until matching incoming message is received on specified client (for cross-client broadcasts). |
| `WAIT` | `WAIT 500ms` | Delays script execution for specified time. |
| `EXPECT_DISCONNECT` | `C1 EXPECT_DISCONNECT` | Asserts that the TCP socket for the client was closed by the server. |
| `EXPECT_CONNECTED` | `C1 EXPECT_CONNECTED` | Asserts that the TCP socket for the client is open and alive. |
| `SEND_RAW` | `C1 SEND_RAW PING\r\n` | Sends exact bytes; no CRLF is appended. |
| `CLOSE_SOCKET` / `RESET` | `C1 CLOSE_SOCKET` | Abruptly closes the peer; `RESET` requests an RST where supported. |
| `CLOSE_WRITE` | `C1 CLOSE_WRITE` | Shuts down only this client’s write side. |
| `RECONNECT` | `C1 RECONNECT` | Closes and reconnects the named peer. |
| `PAUSE` / `RESUME` | `C1 PAUSE` | Stops/starts reading while the TCP peer remains connected. |
| `FLOOD` | `C1 FLOOD 50 PRIVMSG #x :x` | Sends a finite bounded sequence (maximum 10,000). |
| `EXPECT_NONE` | `C1 EXPECT_NONE 200ms` | Requires no queued response during the quiet window. |
| `EXPECT_COUNT` | `C1 EXPECT_COUNT 2 * PRIVMSG *` | Checks the count of queued matches. |
| `TIMEOUT` | `TIMEOUT 750ms` | Sets the default timeout for subsequent assertions. |

---

## 4. Log File Specification (`test_name.log`)

* **Log File Name**: Automatically generated matching the spec name (`<spec_basename>.log`).
* **Format**: All sent, received, and error events are logged sequentially with verbatim payload text.

### Log Prefix Formats
* Outgoing client packet: `<CLIENT> SEND <RAW_TEXT>`
* Outgoing raw packet: `<CLIENT> SEND_RAW <RAW_TEXT>`
* Incoming server packet: `<CLIENT> RECV <RAW_TEXT>`
* System / Internal socket check: `<CLIENT> SYS <INFO>`
* Assertion / Timeout / Disconnect error: `<CLIENT> ERROR <DETAILS>`

---

## 5. Test Scenarios

### Scenario A: Registration Password Failure (`test_pass_failure.spec`)
```text
CLIENTS C1

C1 SEND PASS WRONGPASSWORD
C1 EXPECT 464 * :Password incorrect
C1 SEND NICK Alice
C1 SEND_RAW USER alice 0 * :Alice\r\n
C1 EXPECT_NONE 200ms
C1 EXPECT_CONNECTED
```

### Scenario B: Fragmented Packet Buffering (`test_fragmentation.spec`)
```text
CLIENTS C1

C1 SEND PASS 1234
C1 SEND_RAW NICK Al
WAIT 200ms
C1 SEND_RAW ice\r\n
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
```

### Scenario C: Invite, Kick, & Socket Check (`test_invite_and_kick.spec`)
```text
CLIENTS C1, C2

# Registration
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 creates channel
C1 SEND JOIN #42

# C1 sets channel invite-only
C1 SEND MODE #42 +i

# C2 attempts join without invite -> asserts error numeric 473
C2 SEND JOIN #42
C2 EXPECT 473 Bob #42 :Cannot join channel (+i)

# C1 invites C2
C1 SEND INVITE Bob #42
C1 EXPECT 341 Alice Bob #42
C2 WAIT_RECV :Alice!* INVITE Bob :#42

# C2 joins successfully
C2 SEND JOIN #42
C1 WAIT_RECV :Bob!* JOIN #42

# C1 kicks C2
C1 SEND KICK #42 Bob :Get out!
C2 WAIT_RECV :Alice!* KICK #42 Bob :Get out!

# Verify C2 was kicked from channel but socket remains connected
C2 EXPECT_CONNECTED
```

### Scenario D: Specific Error Expectation (`test_specific_response.spec`)
```text
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 sets channel key (+k secret)
C1 SEND JOIN #protected
C1 SEND MODE #protected +k secret

# C2 tries joining without key -> asserts error numeric 475
C2 SEND JOIN #protected
C2 EXPECT 475 Bob #protected :*
```
