# Tester Framework Testing Strategies & Edge Case Coverage

This document outlines the concrete testing strategies and tools implemented to address all framework limitations and edge cases.

---

## Testing Strategy Matrix & Implementation Status

| # | Edge Case / Feature Gap | Implemented Approach | Implementation Component | Status |
|---|---|---|---|:---:|
| **1** | **Hex/Binary Escape in `SEND_RAW`** (`\x00`, `\0`) | **Extended `testrunner.cpp`** | `testrunner.cpp::decode_raw_escapes` + [50_embedded_null_byte_and_hex_escapes.spec](file:///home/tbatis/core/berg/tester/scenarios/EDGECASE/50_embedded_null_byte_and_hex_escapes.spec) | ✅ Complete |
| **2** | **Server CLI & Process Lifecycle Probes** (Exit codes, bad args, EADDRINUSE, SIGINT/SIGTERM) | **Dedicated Script Suite** | [test_server_lifecycle.sh](file:///home/tbatis/core/berg/tester/test_server_lifecycle.sh) (`make lifecycle`) | ✅ Complete |
| **3** | **Send Buffer Saturation & Flow Control Oracles** (`EAGAIN`/`EWOULDBLOCK`) | **Extended `testrunner` + `SET_SOCK_RCVBUF`** | `testrunner.cpp` + [51_socket_rcvbuf_backpressure.spec](file:///home/tbatis/core/berg/tester/scenarios/EDGECASE/51_socket_rcvbuf_backpressure.spec) | ✅ Complete |
| **4** | **Unbounded Stream & Memory Growth Probes** (Slowloris, Buffer Bomb) | **Resource & Memory Probe Script** | [test_memory_dos.py](file:///home/tbatis/core/berg/tester/test_memory_dos.py) | ✅ Complete |
| **5** | **Multi-Threaded Concurrency Barriers for Race Conditions** | **Dedicated Multi-Threaded C++ Program** | [concurrency_tester.cpp](file:///home/tbatis/core/berg/tester/concurrency_tester.cpp) (`make concurrency`) | ✅ Complete |
| **6** | **Queue Isolation for `EXPECT_NONE` / `EXPECT_COUNT`** | **Extended `testrunner.cpp`** | `testrunner.cpp::assert_none` queue index capture | ✅ Complete |
| **7** | **Improved Failure Diagnostics** | **Extended `testrunner.cpp`** | `testrunner.cpp::format_queue_dump` (line numbers, diffs, queue dumps) | ✅ Complete |

---

## Detailed Component Specifications

### 1. Hex/Binary Escape Decoding in `SEND_RAW`
* **Mechanism:** `decode_raw_escapes()` in `testrunner.cpp` parses `\xHH` hex escapes (e.g., `\x00`, `\x01`, `\xff`) and `\0` null bytes into binary payloads.
* **Usage:** `C1 SEND_RAW NICK al\x00ice\r\n`

### 2. Server CLI & Process Lifecycle (`test_server_lifecycle.sh`)
* **Mechanism:** Subprocess execution harness testing argument counts, non-numeric and out-of-range ports (<1024 without root, negative, >65535), `EADDRINUSE` port collision prevention, and `SIGTERM`/`SIGINT` socket reuse.
* **Run:** `./test_server_lifecycle.sh` or `make lifecycle` from `tester/`.

### 3. Non-Blocking Send Buffer Saturation (`SET_SOCK_RCVBUF` + `PAUSE`)
* **Mechanism:** Directives `SET_SOCK_RCVBUF <bytes>` shrink the client socket's TCP window, while `PAUSE` halts reading, allowing other clients to flood the server and verify that server event loop remains non-blocking.
* **Usage:**
  ```text
  C1 SET_SOCK_RCVBUF 1024
  C1 PAUSE
  C2 FLOOD 50 PRIVMSG #chan :...
  C3 SEND PING :alive
  C3 EXPECT PONG * :alive
  ```

### 4. Unbounded Stream & Server Memory Growth (`test_memory_dos.py`)
* **Mechanism:** Streams multi-megabyte payloads without `\r\n` and monitors server process `VmRSS` via `/proc/<pid>/status` while verifying that concurrent connections remain responsive.
* **Run:** `./test_memory_dos.py [--port <port>] [--pid <pid>]` or `make memory` from `tester/`.

### 5. Multi-Threaded Concurrency Harness (`concurrency_tester.cpp`)
* **Mechanism:** Spawns N parallel OS threads synchronized with `pthread_barrier_t` to trigger microsecond race conditions:
  - **Nickname Collision Race:** 50 threads simultaneously submit `NICK winner` + `USER winner 0 * :winner` after sending `PASS`; asserts exactly 1 winner receives `001 RPL_WELCOME` and 49 receive numeric `433` collision responses.
  - **Burst Accept Queue:** 100 threads connect in parallel within a 10ms window; asserts server accepts all connections without dropping or hanging the event loop.
  - **Simultaneous Channel Mode / Join Race:** 20 threads simultaneously join `#race` and attempt `MODE #race +k secret` or `MODE #race +i`; verifies state consistency, channel operator privilege boundaries, and zero data races or corrupted member lists.
* **Run:** `./concurrency_tester [--threads <count>] [--suite <nick|burst|channel|all>]` or `make concurrency` from `tester/`.


