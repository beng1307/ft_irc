# Tester framework backlog

This file records limitations in the test framework itself. It does not list
server defects or prescribe server behavior.

## Correctness and oracle work

- Define queue boundaries for `EXPECT_NONE` and `EXPECT_COUNT`. Both currently
  inspect all already-queued lines, so a prior reply can affect a later
  assertion. Add an explicit queue-drain/mark directive, or make each oracle
  consider only data received after the assertion starts.
- Improve failures with directive name, client, expected value, observed lines,
  and spec location. Invalid durations and malformed `EXPECT_COUNT` arguments
  should be rejected with a clear parse error.
- Make raw-byte handling fully specified. `SEND_RAW` now decodes `\\r`, `\\n`,
  and `\\\\`; decide how invalid escapes should behave.

## Lifecycle and repeatability

- Replace the fixed server-start delay with a connection/readiness probe and
  fail immediately if the child server exits.
- Give each test a clean, unique log path and optionally preserve server stdout
  and stderr with the corresponding scenario log.
- Add per-scenario setup/teardown hooks, including an optional isolated server
  process, so tests cannot leak state into one another.
- Document platform behavior for `RESET`, `CLOSE_WRITE`, and paused reads;
  these depend on socket and kernel behavior.

## Future coverage capabilities

- Support exact response ordering and explicit queue draining for multi-reply
  IRC commands.
- Add bounded concurrent actions and deterministic synchronization barriers for
  race-sensitive cases.
- Add controlled large-line, malformed-frame, and property/fuzz input support,
  with strict resource caps and reproducible seeds.
- Add optional server-state probes only if protocol-level observations cannot
  express a required evaluator contract.
