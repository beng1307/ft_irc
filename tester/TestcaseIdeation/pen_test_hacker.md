# Adversarial & Stress Testing Ideation (`pen_test_hacker.md`)

## 1. Adversarial Testing Philosophy

Standard test suites verify the **happy path** and predictable error paths (e.g., verifying that sending the wrong password returns `464`). 

An **adversarial testing (pentesting/fuzzing) mindset** flips this assumption:
> *"Assume the client is intentionally hostile, malformed, erratic, or operating in worst-case network conditions. Our goal is to provoke crashes (SIGSEGV, SIGABRT), infinite loops / deadlocks (stuck `poll()`), memory leaks, iterator invalidation, state desynchronization, resource exhaustion, or security bypasses."*

---

## 2. Attack Vectors & Edge-Case Catalog

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Adversarial Attack Surface (ft_irc)                  │
├──────────────────────────────────┬─────────────────────────────────────┤
│ 1. Memory & Iterator Safety      │ 4. Protocol Fuzzing & Malformed I/O │
│    - Iterator invalidation       - Colon explosion (`::::`)            │
│    - Dangling client pointers    - 0-byte delimiters & control chars   │
│    - Channel deletion race       - 10,000 parameter overflow           │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 2. State Machine Inversions      │ 5. Resource Exhaustion & DoS        │
│    - Unregistered command floods - Giant lines (>64 KB without CRLF)   │
│    - Re-registration hijack      - Rapid connection/reset churning     │
│    - Dynamic nick swap hijacking - Zero-window / blocked write socket  │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 3. Channel Privilege Boundary    │ 6. TCP Stream Splitting Torture     │
│    - Last-op suicide / deop      - Split between `\r` and `\n`         │
│    - Mode flag parameter skew    - Byte-drip / Slowloris stream        │
│    - Case sensitivity collisions - Rapid pipelined bursts              │
└──────────────────────────────────┴─────────────────────────────────────┘
```

---

### Category A: Memory Safety, Dangling Pointers & Iterator Invalidation (CRASH / SEGV)

C++98 IRC servers manage dynamic collections (`std::vector`, `std::map`, `std::list`) of clients and channels. Modifying these collections while iterating over them or holding raw pointers/references is the #1 cause of fatal segfaults.

| ID | Attack Vector / Scenario | Malicious Input / Execution Sequence | Target Vulnerability & Expected Defense |
| :--- | :--- | :--- | :--- |
| **ADV-MEM-01** | **Broadcast Iterator Invalidation on Disconnect** | C1 and C2 join `#chan`. C1 sends `PRIVMSG #chan :flood`. While server iterates over channel members to send to C2, C2 abruptly drops connection (`RST`). | Server loop iterating over channel sockets must not dereference erased client pointers or crash when `send()` fails on a dead socket. |
| **ADV-MEM-02** | **Self-Kicking / Self-Part During Broadcast** | Op C1 executes `KICK #chan C1 :bye` or `PART #chan`. Channel now has 0 members and is deleted during the execution of the command itself. | Server must cleanly delete the channel container without referencing freed memory or invalidating parent channel-map iterators. |
| **ADV-MEM-03** | **Simultaneous Channel Destruction & Member Cleanup** | C1 is in `#chan1`, `#chan2`, `#chan3`. C1 sends `QUIT`. The server cleans up C1 from all three channels. `#chan2` was only occupied by C1 and gets destroyed. | Channel destruction must not corrupt client's list of joined channels or leave dangling channel references in the client object. |
| **ADV-MEM-04** | **Reusing Sockets on Rapid Recycled Descriptors** | C1 connects (fd 4), disconnects abruptly. C2 immediately connects and OS assigns recycled fd 4. Server receives lingering data. | Server must completely flush and reset per-client buffers so C2 does not inherit C1's unparsed residual buffer. |
| **ADV-MEM-05** | **Double Registration / Overwriting Active Client Struct** | Client sends `PASS`, `NICK`, `USER`, gets `001`, then rapidly sends another `USER` with different usernames. | Must not re-allocate or re-initialize internal buffers; must reject with `462 ERR_ALREADYREGISTRED` without memory leaks. |

---

### Category B: Protocol Fuzzing, String Splitting & Parameter Skew (PARSER TORTURE)

Adversarial clients intentionally break RFC formatting rules to probe array bounds, index parsing, string tokenizers, and sub-string extraction.

| ID | Attack Vector / Scenario | Malicious Input / Execution Sequence | Target Vulnerability & Expected Defense |
| :--- | :--- | :--- | :--- |
| **ADV-FUZZ-01** | **Leading, Trailing & Consecutive Colon Spam** | `::::PRIVMSG :::: #chan ::::::hello ::::world:::` or `:::NICK :::Alice` | Parser must correctly identify command and parameters without crashing on empty tokens or extracting empty command names. |
| **ADV-FUZZ-02** | **Massive Parameter Overflow (>100 params)** | `JOIN #c1 #c2 #c3 ... #c500` or `MODE #c +i +t +k a b c d e f g h i j k ...` | Parser vector must not overflow stack/heap or cause integer overflow in parameter indexing. |
| **ADV-FUZZ-03** | **Empty Delimiters & Bare Whitespace Floods** | `\r\n`, `    \r\n`, `\t\t \t\r\n`, `PRIVMSG      #c      :msg` | Server must safely ignore empty lines and collapse multiple consecutive whitespace delimiters without throwing exceptions. |
| **ADV-FUZZ-04** | **Mode Flag & Parameter Mismatch (Under/Over-flow)** | `MODE #chan +itklo` (5 flags, 0 parameters) vs `MODE #chan +k` vs `MODE #chan -l 100` | Flags requiring parameters (`+k`, `+o`, `+l`) must not read past the end of the argument vector (`std::vector::operator[]` out-of-bounds). |
| **ADV-FUZZ-05** | **Integer Overflow in Limit Mode (`+l`)** | `MODE #chan +l 99999999999999999999999` or `MODE #chan +l -42` or `MODE #chan +l 0` | Must not throw unhandled `std::out_of_range` on `std::atoi`/`strtol`; must handle non-positive/overflowing limits cleanly. |
| **ADV-FUZZ-06** | **Trailing Split on Exact CRLF Boundary** | Packet 1: `PRIVMSG #chan :hello\r`<br>Packet 2: `\n` | Buffer aggregator must not discard `\r` or treat `\r` as part of the message trailing payload. |
| **ADV-FUZZ-07** | **Giant Line Buffer DoS (>64 KB without CRLF)** | Client sends 64 KB of `AAAAA...` with no `\n`. | Server must not allocate infinite memory in client receive buffer; must enforce maximum line bounds or truncate safely. |
| **ADV-FUZZ-08** | **Non-Printable & Binary Control Characters** | `NICK \x01\x02\xFF\x7F` or `PRIVMSG #chan :\x00\x01\x02\r\n` | Must not treat null bytes (`\0`) as premature C-string terminators causing buffer length desyncs. |

---

### Category C: State Machine Desynchronization & Privilege Attacks (LOGIC ABUSE)

Adversaries try to exploit logical oversights in state transitions to perform actions without permission or leave the server in a zombie state.

| ID | Attack Vector / Scenario | Malicious Input / Execution Sequence | Target Vulnerability & Expected Defense |
| :--- | :--- | :--- | :--- |
| **ADV-STATE-01** | **Unauthenticated Command Gating Probe** | Fresh connection sends `JOIN #secret`, `MODE #secret +o Me`, `PRIVMSG #secret :hi`, `TOPIC #secret :t` before `PASS`. | Server must reject all with `451 ERR_NOTREGISTERED` and not leak channel existence or topic data. |
| **ADV-STATE-02** | **Pre-Auth Nick Hijack / Nick Claim Before Password** | C1 sends `NICK Admin`, does NOT send `PASS`. C2 sends `PASS`, `NICK Admin`. | Unauthenticated client C1 must either be rejected or timed out; must not prevent valid clients from registering if C1 failed `PASS`. |
| **ADV-STATE-03** | **Rapid Nick Change Ping-Pong Collision** | C1 (`Alice`) and C2 (`Bob`). C1 sends `NICK Bob` at the exact same moment C2 sends `NICK Alice` in pipelined packets. | State lookup table must avoid deadlock or dual-ownership; both must receive appropriate `433` or clean swap without collision. |
| **ADV-STATE-04** | **Last-Operator Self-Demotion / Abandonment** | C1 is the only operator on `#chan`. C1 executes `MODE #chan -o C1`. | Channel now has 0 operators. Server must either allow it gracefully or handle subsequent operator commands with `482` without getting stuck. |
| **ADV-STATE-05** | **Invite Bypass via Case Insensitivity Collision** | `#Channel` has mode `+i`. C1 is invited to `#channel`. C1 sends `JOIN #CHANNEL`. | Channel names are RFC-case-insensitive (`#channel` == `#CHANNEL`). Server must recognize the invite token regardless of letter casing. |
| **ADV-STATE-06** | **Channel Key Bypass via Empty/Whitespace Keys** | Op sets `MODE #chan +k " "`. Target tries `JOIN #chan`. | Server must handle whitespace keys consistently without allowing empty-string bypasses. |
| **ADV-STATE-07** | **Ghost Channel Re-creation Hijack** | C1 (`+o`) and C2 are in `#chan`. C1 leaves (`PART`). C2 is regular user. C1 immediately rejoins `JOIN #chan`. | C1 must NOT automatically become operator again because channel already exists (occupied by C2). |

---

### Category D: Concurrency, Event Loop Deadlocks & Network Abuse (STALL / FREEZE)

Evaluators and hostile environments will test if one misbehaving client can degrade or freeze the service for all other clients.

| ID | Attack Vector / Scenario | Malicious Input / Execution Sequence | Target Vulnerability & Expected Defense |
| :--- | :--- | :--- | :--- |
| **ADV-NET-01** | **Slowloris / Byte-Drip Attack** | Client opens connection and sends 1 byte every 500ms (`N` ... `I` ... `C` ... `K` ...). | Server must not block on `recv()` or freeze the single `poll()` loop; other clients must experience zero latency. |
| **ADV-NET-02** | **Blocked Outbound Socket (Zero-Window / `SIGSTOP`)** | C1 and C2 in `#chan`. C2 is paused (`SIGSTOP`). C1 floods 500 messages to `#chan`. Server outbound buffer for C2 fills up (`EWOULDBLOCK` / `EAGAIN`). | Server must NOT block on `send()` or crash. It must buffer outbound data or handle non-blocking writes gracefully without halting C1. |
| **ADV-NET-03** | **Rapid Connection / Reset Storm (FD Churn)** | Script opens 50 TCP connections and instantly closes them with `SO_LINGER(0)` (`RST`) in 100ms. | Server `accept()` loop must handle `ECONNABORTED` cleanly and maintain socket table integrity. |
| **ADV-NET-04** | **Pipelined Multi-Command Bomb** | Client sends 50 valid commands concatenated in a single 2 KB `send()` packet (`JOIN #a\r\nPRIVMSG #a :1\r\nPART #a\r\n...`). | Server must parse and execute all 50 sequentially without buffer corruption or truncation. |
| **ADV-NET-05** | **Unexpected Mid-Command FIN** | Client sends `PRIVMSG #chan :half_message_without_crlf` and immediately calls `close()`. | Server must detect EOF (`recv == 0`), clean up client state, and not broadcast corrupted half-messages to peers. |

---

## 3. High-Priority Adversarial Scenarios to Implement

The following test scenarios are constructed under `tester/scenarios/adversarial/` using the `.spec` test harness to validate these adversarial cases:

1. **`scenarios/adversarial/34_parser_colon_and_spaces.spec`**:
   - Tests excessive colons (`::::`), excessive tabs/spaces between arguments, trailing colon edge cases, and CRLF packet splitting.
2. **`scenarios/adversarial/35_unregistered_attack_surface.spec`**:
   - Floods commands (`JOIN`, `MODE`, `TOPIC`, `KICK`, `INVITE`, `PRIVMSG`) before sending `PASS`/`NICK`/`USER` to verify zero state leakage and strict `451` errors, plus double registration protection (`462`).
3. **`scenarios/adversarial/36_mode_parameter_skew_fuzz.spec`**:
   - Tests `MODE` flag mismatches (`+itklo`, `+l -42`, `+l 0`, `+k` with missing param, `-o` without target) and last-operator self-demotion behavior.
4. **`scenarios/adversarial/37_abrupt_disconnect_during_traffic.spec`**:
   - Active channel with 4 clients; clients drop abruptly (`RESET` / `CLOSE_SOCKET`) during active broadcasts, solo channel destruction, and mid-command EOF without CRLF.
5. **`scenarios/adversarial/38_pipelined_storm.spec`**:
   - Pipelined commands packed into a single raw TCP buffer, bounded message floods, and multi-channel parameter lists.
6. **`scenarios/adversarial/39_invite_and_privilege_boundaries.spec`**:
   - Tests ghost channel re-creation hijack prevention, operator privilege boundaries, and channel name case-insensitivity on invitations.
