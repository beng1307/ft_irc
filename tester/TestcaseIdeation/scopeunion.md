# Scope Union: Status Quo vs. Project Requirements (ft_irc)

## 1. Overview & Methodology

This document bridges the **Standard IRC Status Quo** (RFC 1459 / RFC 2812) defined in [statusquo.md](file:///home/tbatis/core/berg/tester/TestcaseIdeation/statusquo.md) and the explicit requirements of the **ft_irc** project defined in [req.txt](file:///home/tbatis/core/berg/DOCS/req.txt), [subject.txt](file:///home/tbatis/core/berg/DOCS/subject.txt), and [eval.txt](file:///home/tbatis/core/berg/DOCS/eval.txt).

The purpose of this mapping is to determine:
1. **Mandatory In-Scope Features**: Behaviors that MUST be fully implemented, compliant, and verified.
2. **Implicit & Reference Client Compatibility Requirements**: Features not explicitly listed as standalone mandatory commands in the brief summary, but strictly necessary for standard IRC clients (e.g. HexChat, WeeChat, irssi, nc) to establish, maintain, and terminate connections without errors or timeouts.
3. **Out-of-Scope / Excluded Protocol Features**: Advanced or multi-server parts of RFC 1459/2812 that are explicitly forbidden or not required.

---

## 2. Comprehensive Scope Classification Matrix

| Feature Area | Status Quo (RFC 1459/2812) | Project Requirements (`DOCS/req.txt`, `eval.txt`) | Scope Classification | Justification & Expected Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Transport & Multiplexing** | Non-blocking TCP, multiplexed connections | Single `poll()` / `epoll()` / `select()`, non-blocking I/O on all sockets, no forking | **MANDATORY CORE** | Must handle multiple concurrent clients, packet fragmentation (nc `com` `man` `d\n`), back-to-back frames, and slow/paused clients without hanging. |
| **Connection Password (`PASS`)** | Optional server/link password | Required on startup `./ircserv <port> <pwd>`, clients must provide matching password | **MANDATORY CORE** | Must validate password before registering client (`464 ERR_PASSWDMISMATCH`). Reject duplicate `PASS` once registered (`462 ERR_ALREADYREGISTRED`). |
| **Nickname Management (`NICK`)** | Unique nick registration, live nick changes, nick collisions | Set nickname during registration, reject duplicate nick, support dynamic changes | **MANDATORY CORE** | Handle missing nick (`431`), erroneous nick (`432`), collision (`433`), and registration pipeline. |
| **User Details (`USER`)** | Username, hostname, servername, realname (`USER <user> <mode> <unused> :<real>`) | Set username during registration | **MANDATORY CORE** | Validates parameters (`461`), prevents re-registration (`462`), completes registration handshakes. |
| **Registration Welcome Banner** | RPL_WELCOME (001), 002, 003, 004 | Reference client connects without error | **MANDATORY COMPATIBILITY** | GUI/CLI clients (HexChat, irssi) require numeric `001` to transition from connecting to connected state. |
| **Keepalive (`PING` / `PONG`)** | `PING <token>` $\to$ `PONG :<token>` heartbeat | Reference client stability, nc verification | **MANDATORY COMPATIBILITY** | Clients routinely send `PING` to check latency; if server fails to answer with `PONG`, clients abort connection. |
| **Capability Negotiation (`CAP`)** | IRCv3 `CAP LS`, `CAP END`, `CAP REQ` | Reference client compatibility | **MANDATORY COMPATIBILITY** | Modern clients send `CAP LS 302` at connect. Server must either reply `CAP * LS :` or ignore/allow registration to complete upon `CAP END`. |
| **Client Disconnect (`QUIT`)** | `QUIT [:<reason>]`, socket close, broadcast to shared channels | Clean disconnection, client cleanup | **MANDATORY CORE** | Frees resources, leaves channels, informs channel peers with `QUIT :reason`, handles abrupt socket closure (EOF/FIN/RST). |
| **Channel Join (`JOIN`)** | `JOIN <chan> [<key>]`, auto-create channel with creator as +o | Join channel, forward messages to all joined clients | **MANDATORY CORE** | Creates channel on first join (grants `@` op), joins existing, broadcasts `JOIN`, sends `RPL_NAMREPLY` (353) & `RPL_ENDOFNAMES` (366). Rejects if key wrong (`475`), limit reached (`471`), or invite-only (`473`). |
| **Channel Leave (`PART`)** | `PART <chan> [:<msg>]` | Leave channel, cleanup state | **MANDATORY CORE** | Removes client from channel, broadcasts `PART` to members, destroys channel if empty. Validates membership (`442`). |
| **Channel Messaging (`PRIVMSG`)** | Send to `#chan`, broadcast to all other members (sender isolated) | Forward all channel messages to every other client joined to channel | **MANDATORY CORE** | Sender does not receive their own message. Validates channel existence (`403`) and membership/permissions (`404`). |
| **Direct Messaging (`PRIVMSG`)** | Send to `<nickname>` (private 1-on-1 message) | Send and receive private messages using reference client | **MANDATORY CORE** | Delivers exclusively to recipient socket. Handles missing recipient (`411`), empty text (`412`), nonexistent user (`401`). |
| **Channel Topic (`TOPIC`)** | View topic, change topic (subject to mode `+t`) | Specific operator command: change or view channel topic | **MANDATORY CORE** | Unset/set topic, query topic (`332` / `331`), restrict modifications to ops if `+t` is active (`482`), allow anyone if `-t`. |
| **Channel Operator Eject (`KICK`)** | `KICK <chan> <user> [:<reason>]` | Specific operator command: Eject a client from the channel | **MANDATORY CORE** | Checks sender is op (`482`), target is on channel (`441`), broadcasts `KICK` notice, updates channel member lists. |
| **Channel Invitation (`INVITE`)** | `INVITE <user> <chan>` | Specific operator command: Invite a client to a channel | **MANDATORY CORE** | Sends `341 RPL_INVITING` to sender, sends `INVITE` notice to target, records invitation for `+i` channel bypass. Validates op status if channel is `+i`. |
| **Channel Mode `i` (Invite-Only)** | `MODE <chan> +i` / `-i` | Set/remove Invite-only channel | **MANDATORY CORE** | Blocks `JOIN` without invite (`473 ERR_INVITEONLYCHAN`), permits join if invited, requires op to set (`482`). |
| **Channel Mode `t` (Topic Lock)** | `MODE <chan> +t` / `-t` | Set/remove restrictions of TOPIC command to channel operators | **MANDATORY CORE** | When `+t`, non-op `TOPIC` returns `482`. When `-t`, non-op can set topic. |
| **Channel Mode `k` (Channel Key)** | `MODE <chan> +k <key>` / `-k [<key>]` | Set/remove the channel key (password) | **MANDATORY CORE** | Enforces key on `JOIN` (`475 ERR_BADCHANNELKEY`), stores key, handles removal. |
| **Channel Mode `o` (Operator Privilege)** | `MODE <chan> +o <user>` / `-o <user>` | Give/take channel operator privilege | **MANDATORY CORE** | Promotes/demotes target member, reflects `@` in `RPL_NAMREPLY`, enforces op permissions. |
| **Channel Mode `l` (User Limit)** | `MODE <chan> +l <num>` / `-l` | Set/remove the user limit to channel | **MANDATORY CORE** | Blocks `JOIN` when active members $\ge$ limit (`471 ERR_CHANNELISFULL`), removes limit with `-l`. |
| **Channel Mode Query (`MODE #chan`)** | Query current modes (`324 RPL_CHANNELMODEIS`) | Expected for client GUI synchronization | **MANDATORY COMPATIBILITY** | Returns active flags (`+itkl`) and params on query. |
| **Global Server Operator (`OPER`/`DIE`/`REHASH`/`KILL`)** | Server administrator management | Forbidden / Not required | **OUT OF SCOPE** | Project strictly requires *channel* operators, not global network IRC operators. |
| **Server-to-Server Linking (`SERVER`/`SQUIT`)** | IRC Network mesh routing | Explicitly forbidden in subject | **OUT OF SCOPE** | Single standalone daemon architecture. |
| **File Transfer / DCC Protocol** | Direct client-to-client or relayed DCC | Extra / not in mandatory subject | **OUT OF SCOPE** | Standard text messaging over IRC is the only requirement. |
| **Advanced Modes (`+m`, `+n`, `+b`, `+s`, `+p`, `+v`)** | Moderated, banlists, secret, voice | Not in mandatory required mode set | **OUT OF SCOPE** | Only `i`, `t`, `k`, `o`, `l` are mandatory. |
| **User Modes (`MODE <nick> +i/w/s/o`)** | User flag modifications | Not in mandatory requirements | **OUT OF SCOPE** | Channel modes are the focus. |

---

## 3. High-Priority Architectural & Robustness Invariants

From Section IV.1 and IV.3 of the Subject and Evaluation Guidelines, the following operational invariants must be validated:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ft_irc Robustness Core                          │
├──────────────────────────────────┬─────────────────────────────────────┤
│ 1. Non-Blocking Single Event Loop│ 4. Slow / Suspended Client Handling │
│    - Only 1 poll()/epoll()/select()  - SIGSTOP (^Z) client buffering   │
│    - Zero blocking I/O calls         - Resuming client drained cleanly │
│    - Non-reliance on errno           - No server stall or freeze       │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 2. Stream Buffer Reconstruction  │ 5. Abrupt Client Teardown           │
│    - Aggregates split chunks (nc)    - Socket EOF / ECONNRESET handled │
│    - Handles back-to-back commands   - Clean channel departure notice  │
│    - Flushes on \r\n / \n            - Complete heap/resource release  │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 3. Connection State Progression  │ 6. Operator Access Control          │
│    - Unregistered command gating     - Strict verification on KICK,    │
│    - Re-registration prevention      - MODE changes, INVITE (+i),      │
│    - Dynamic nick broadcast update   - and TOPIC (+t)                  │
└──────────────────────────────────┴─────────────────────────────────────┘
```

---

## 4. Key Takeaways & Scope Synthesis

1. **`PING` and `PONG` are fundamentally mandatory in scope**: Even though `req.txt` highlights high-level channel operations, reference clients (HexChat, irssi, WeeChat) cannot stay connected without `PING`/`PONG` and basic `CAP` negotiation.
2. **5 Mandatory Modes**: Exactly `i`, `t`, `k`, `o`, `l` must be supported with full parameter parsing, validation, error replies, and mode queries (`324`).
3. **Channel Operator Hierarchy**: Every channel must maintain creator-as-op, promotion/demotion via `MODE +o/-o`, and privilege checks (`482 ERR_CHANOPRIVSNEEDED`) on `KICK`, `TOPIC` (+t), `MODE`, and `INVITE` (+i).
4. **Resilience under Adversity**: The test suite must rigorously test network anomalies (split packets, multiple commands in one buffer, sudden disconnects, unauthenticated floods, paused clients).
