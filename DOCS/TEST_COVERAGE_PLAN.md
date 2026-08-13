# ft_irc adversarial test-coverage plan

This is the implementation backlog for the integration tester. It deliberately
contains test ideas and oracle definitions, not new `.spec` sequences or runner
changes.

## Verified scope and assumptions

- The official materials used for this verification are in the sibling 42
  checkout at
  `42Vienna/IRC/DOCS/subject.txt`, `req.txt`, and `eval.txt`. They require a
  C++98 TCP IRC server that handles multiple clients, authentication,
  NICK/USER identity, channels, private messages, and channel broadcasts to
  every other member.
- The subject explicitly requires all five channel modes: `i` invite-only, `t`
  topic restriction, `k` channel key, `o` operator grant/take, and `l` channel
  user-limit set/remove. User-limit coverage is mandatory, not optional.
- The subject requires KICK, INVITE, TOPIC (change/view), and MODE. The
  evaluator requires channel-operator actions to be tested for regular users
  and operators.
- The evaluator explicitly requires partial/low-bandwidth commands, unexpected
  client termination including half a command, continued service for other/new
  clients, and a suspended client with channel flooding.
- No `eval` or `req` file is currently present in this worktree or in the
  `/Users/timar/code/42/ft_irc` checkout; if copies are later added to this
  repository, re-check this document against those local copies and treat
  `eval` as authoritative over the shorter requirements text.
- The configured server password is supplied as a command-line argument. The
  current runner connects to one host/port and cannot vary that password except
  by sending `PASS` after connecting.
- Existing expected behavior is based on the implementation and runner
  documentation. The subject does not prescribe every exact numeric or
  malformed-command policy, so those details must be confirmed against the
  reference client/evaluator before becoming strict oracles.
- Every multi-client case should verify both the initiating client and all
  affected/non-affected clients, then verify socket liveness. A passing numeric
  alone is not enough when a broadcast or membership mutation is the real
  contract.

## Status legend

| Status | Meaning |
| --- | --- |
| **Covered** | An existing scenario exercises the pathway; strengthen its oracle only if noted. |
| **DSL-now** | Expressible with `SEND`, `F SEND`, `EXPECT`, `WAIT_RECV`, `WAIT`, and connection assertions, but no scenario currently covers it. |
| **DSL-gap** | Meaningful, but current matching/transport semantics make it impossible or unreliable to assert. |
| **Framework-later** | Capability worth adding after the backlog of DSL-now cases. |

## Existing coverage inventory

| Suite/folder | Current scenarios | Covered behavior and gaps |
| --- | --- | --- |
| `registration/` | `01_pass_failure`, `02_fragmentation`, `03_basic_registration` | Correct PASS success/failure, fragmented NICK buffering, registration, duplicate-client messaging setup. The failure case does not assert the documented disconnect despite the scenario documentation showing it. |
| `messaging/` | `03_basic_registration`, `04_channel_join_and_broadcast`, `10_client_disconnect` | User-to-user, channel broadcast to another member, QUIT broadcast, and one socket-liveness check. No negative recipient/text/unknown-target cases. |
| `channels/access/` | `04`, `05`, `06`, `07` | Create/join, invite-only, key, user limit, invite then join, kick. No PART, rejoin-after-kick, mode removal, or invalid channel names. |
| `channels/topic/` | `08` | +t restriction and topic broadcast. No topic query/empty topic, missing channel, or persistence after PART/rejoin. |
| `channels/ops/` | `09` | Non-op rejection, +o, then operator KICK. No -o, operator handoff/removal, or invalid target paths. |
| `lifecycle/` | `10` | QUIT and client socket closure. No abrupt peer close, channel cleanup, or later nick reuse. |

## Proposed suites and case map

The names are proposed folders/case families; implementation can choose exact
filenames. Each row is an adversarial stateful sequence, followed by its oracle.

### `registration/`

| Status | Sequence / oracle |
| --- | --- |
| **DSL-now** | PASS with no argument, USER with no argument, and NICK with no argument: assert `461`/`431`; socket remains connected. |
| **DSL-now** | Wrong PASS followed by correct PASS, NICK, USER: verify whether recovery is permitted by the evaluator; current code permits a later correct PASS. |
| **DSL-now** | NICK/USER/PASS in every order, including PASS last; assert exactly one welcome burst and no duplicate registration. |
| **DSL-now** | Register without PASS, or with only NICK/USER: assert no `001`, no channel/message access, and connection policy required by subject. |
| **DSL-now** | Duplicate NICK from C2 while C1 is registered (`433`), then C2 chooses a new nick and completes registration. |
| **DSL-now** | Re-register after `001` with PASS/USER/NICK: assert `462` where required and no identity corruption. |
| **DSL-now** | Case-insensitive command names and fragmented CRLF across PASS/USER/NICK; assert one command per line. |
| **DSL-gap** | Assert “no response within a bounded interval” and exact welcome ordering; `WAIT_RECV` can prove presence but has no negative/silence or ordering primitive. |
| **Framework-later** | Start the server with a deliberately wrong configured password and test a valid client PASS (`464`), then repeat with the correct password. This requires a per-test server-process/configuration hook, not a new IRC command. |

### `messaging/`

| Status | Sequence / oracle |
| --- | --- |
| **DSL-now** | `PRIVMSG` unknown nick (`401`), unknown channel (`403`), no recipient (`411`), and no text (`412`). |
| **DSL-now** | Channel PRIVMSG from a non-member and after KICK: assert error/no delivery to members. |
| **DSL-now** | Three clients: sender, recipient, observer. Verify direct message reaches only recipient and channel message reaches every other member, while an unrelated observer receives nothing. |
| **DSL-now** | Messages containing spaces, colon, punctuation, empty trailing text, long payload, and command-like text; assert payload preservation and no command injection. |
| **DSL-now** | Lowercase `privmsg`, nick changes before messaging, and target nick that is a prefix of another nick. |
| **DSL-gap** | Prove absence of delivery to an observer and distinguish one broadcast from duplicated packets; no negative receive/assert-count primitive. |
| **Framework-later** | Add `EXPECT_NONE`/quiet-window and receive-count or queue-drain assertions; add raw-byte payload support for embedded CR/LF and boundary fuzzing. |

### `channels/membership/`

| Status | Sequence / oracle |
| --- | --- |
| **Covered** | Join broadcast and initial channel creation are covered by `04`; invite-only/key/limit joins by `05`–`07`. |
| **DSL-now** | PART a joined channel with and without a reason; all members receive the PART form required by subject, sender is removed, and sender can rejoin. |
| **DSL-now** | PART unknown channel (`403`) and PART while not a member (`442`); socket remains connected. |
| **DSL-now** | JOIN an already joined channel; assert no duplicate membership/broadcast or document implementation-specific behavior. |
| **DSL-now** | Join nonexistent/nonstandard names (`#`, `#a`, `#a,b`, spaces, `&local`) and malformed/multiple parameters; compare with subject constraints. |
| **DSL-now** | Kick, then attempt PRIVMSG/PART/rejoin; ensure kicked client is removed but TCP remains usable and invite state is handled correctly. |
| **DSL-gap** | Assert channel deletion after the last member leaves and absence of stale state on a later channel recreation; current DSL cannot reliably observe absence/stale broadcasts. |
| **Framework-later** | Add server reset/isolation and explicit channel-state introspection only if evaluator tests require lifecycle assertions across independent runs. |

### `channels/modes/`

| Status | Sequence / oracle |
| --- | --- |
| **Covered** | +i, +k, +l, +t, and +o positive/negative paths are covered by `05`–`09`. |
| **DSL-now** | Query `MODE #chan` after each mode; assert `324` and parameters, including combinations and removal. |
| **DSL-now** | Remove `-i`, `-k`, `-l`, `-t`, and `-o`; verify access immediately changes and broadcasts reach members. |
| **DSL-now** | Non-member and non-operator MODE attempts (`442`/`482`), unknown mode (`472`), missing mode arguments (`461`), nonexistent channel (`403`). |
| **DSL-now** | Multi-flag strings, repeated signs, unsupported flags, invalid/zero/negative/non-numeric limits, and key containing punctuation. Assert no partial state mutation unless specified. |
| **DSL-now** | +o/-o for unknown nick (`401`) and nick not on channel (`441`); operator demotion and transfer must not accidentally grant privileges. |
| **DSL-gap** | Assert that a malformed multi-mode command leaves all earlier flags unchanged when the evaluator requires atomicity; current protocol matcher cannot inspect state without follow-up cases and cannot assert silence/order robustly. |
| **Framework-later** | Add reusable state predicates/sequence variables (e.g. query mode and compare normalized sets) and exact response queues for multi-reply commands. |

### `channels/invite-topic/`

| Status | Sequence / oracle |
| --- | --- |
| **DSL-now** | INVITE unknown nick (`401`), non-member inviter (`442`), non-op inviter (`482`), already-present target (`443`), missing args (`461`), and nonexistent channel (`403`). |
| **DSL-now** | Invite a client, disable/enable +i, consume invite by joining, then retry join; verify invite is single-use and target receives the asynchronous INVITE only once. |
| **DSL-now** | TOPIC query on unset/set topic (`331`/`332`), empty topic, non-member (`442`), missing channel (`403`), missing args (`461`), and +t non-op rejection (`482`). |
| **DSL-now** | Set topic, PART/rejoin, and query from another member; verify persistence and exact trailing-parameter handling. |
| **DSL-gap** | Ensure an unauthorized TOPIC produces no broadcast to other members; needs a negative receive assertion. |

### `lifecycle/transport/`

| Status | Sequence / oracle |
| --- | --- |
| **Covered** | Graceful QUIT and fragmented NICK are covered by `10` and `02`. |
| **DSL-now** | Send several commands in one TCP write (the DSL appends CRLF per SEND), fragmented commands with multiple lines in one remainder, blank lines, and missing final CRLF. |
| **DSL-gap** | Abruptly kill/close a client after joining and after sending half a command; verify remaining and newly connected clients continue normally. The evaluator explicitly requires this, but the current spec language has no peer-kill/half-close directive. |
| **DSL-gap** | Suspend one client and flood a channel from another, then resume it and verify the server does not hang and queued processing remains correct. This needs process/signal control and bounded flood generation outside the current DSL. |
| **DSL-now** | PING/PONG and unknown command behavior, if required by the subject; current dispatch has no explicit PING/PONG handler, so record observed evaluator expectation before strict assertions. |
| **DSL-now** | QUIT with/without reason, QUIT while in multiple channels, and client reconnect/nick reuse after close. |
| **DSL-gap** | Half-close, RST, delayed packet interleavings, server-side backpressure, exact packet boundaries, and timing/race reproducibility are not controllable by the script language. |
| **Framework-later** | Raw socket directives (`SEND_RAW`, half-close, reconnect), peer kill/suspend/resume controls, bounded flood generation, configurable per-step timeout, deterministic concurrent clients, and property/fuzz input generation. |

## Cross-cutting error and security probes

These should be run against every command family where applicable:

- missing, extra, and reordered parameters; empty trailing parameter; tabs and
  repeated spaces;
- mixed case commands and nick/channel case behavior;
- very long lines and messages near buffer boundaries;
- CR, LF, and CRLF injection attempts inside trailing text;
- unknown nick/channel, non-member, non-operator, duplicate action, and action
  after disconnect;
- client isolation: one malformed or unauthorized client must not disconnect or
  mutate another client;
- resource behavior: many clients, repeated joins/parts, repeated mode changes,
  and connections that never finish registration (bounded stress only).

The current DSL can express most single-threaded variants with `F SEND` plus
`EXPECT`; it cannot reliably express volume, randomness, timing races, or
negative delivery. Those belong in the framework-later backlog rather than
pretending that a timeout is a protocol oracle.

## Verification strategy before implementation

1. Use the verified subject/evaluator materials as the requirement baseline;
   when local `eval` and `req` copies are added, prefer `eval` and mark each row
   with the evaluator’s exact numeric, prefix, trailing text, and connection
   policy.
2. Run the existing ten scenarios unchanged against a clean server build;
   preserve their logs as the baseline and fix documentation mismatches (for
   example, `01_pass_failure` documents an expected disconnect but does not
   contain `EXPECT_DISCONNECT`).
3. Implement **DSL-now** cases in small isolated specs, one state transition per
   assertion cluster, using exact `EXPECT` patterns for numerics and
   `WAIT_RECV` for asynchronous broadcasts.
4. For each negative case, verify both “error received by actor” and “no state or
   delivery change” using a later positive/query action where possible. Label the
   result **DSL-gap** when that second half cannot be observed.
5. Run each spec repeatedly, inspect chronological logs for stale queued replies,
   and test under slow and fast loopback conditions. Treat flaky timing as a
   framework defect, not a server pass.
6. Only after the deterministic backlog is complete, prioritize framework work:
   server-process/password configuration, negative receive/count assertions,
   peer kill/suspend/flood controls, raw transport controls, concurrency, and
   fuzzing.

## Implementation order

1. Registration and command-parameter errors.
2. PART, rejoin, kick cleanup, and direct/channel negative messaging.
3. MODE queries/removals and all operator/error branches.
4. INVITE/TOPIC negative and persistence cases.
5. Transport/lifecycle edge cases and cross-client isolation.
6. Framework-later capabilities and bounded stress/fuzz suites.
