### RUN SERVER

`./ircserv 6667 1234`

### TESTER FOLDER

`cd tester`

### MAKE TESTER

`make`

### TEST CATALOG

See [scenarios/README.md](scenarios/README.md) for the complete coverage map.
Specs may live in nested suite folders; `run_scenarios` discovers them recursively.
See [TESTER_TODO.md](TESTER_TODO.md) for known framework limitations and next
steps.

### RUN ALL TESTS

`make run`

### RUN A SINGLE TEST

`make run 5`

### ADD NEW TEST

Create the file in the suite folder that matches its protocol area, for
example `scenarios/registration/ID_new_test_sequence.spec`.

### ADVERSARIAL DIRECTIVES

The supported directives include `SEND_RAW`, `CLOSE_SOCKET`, `CLOSE_WRITE`, `RESET`,
`RECONNECT`, `PAUSE`, `RESUME`, `FLOOD count payload`, `EXPECT_NONE duration`,
`EXPECT_COUNT n pattern`, and `TIMEOUT duration`. The old `SENDPART` spelling
has been replaced by `SEND_RAW`. In `SEND_RAW`, use `\\r`, `\\n`, and `\\\\` to send carriage
return, newline, and backslash bytes respectively.

Traffic generation is finite and capped at 10,000 lines. `RESET` requests an
RST with `SO_LINGER(0)` where supported; packet boundaries and unbounded fuzzing
are deliberately outside the framework contract. Server lifecycle remains
external by default for backwards compatibility; set `SERVER_BIN`, `PASSWORD`,
and optional `SERVER_EXTRA_ARGS` to let `run_scenarios` launch and clean up an
isolated server. `HOST`, `PORT`, and `TESTRUNNER_BIN` remain configurable.
