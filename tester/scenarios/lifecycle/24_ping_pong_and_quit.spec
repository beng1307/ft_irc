# Tests PING/PONG keepalive replies, trailing colon token parsing, bare QUIT, and pre-registration QUIT.
CLIENTS C1, C2, C3

# LIFE-07: Pre-registration QUIT -> Socket closes cleanly without error
C1 SEND QUIT
C1 EXPECT_DISCONNECT

# Register C2 and C3
C2 SEND PASS 1234
C2 SEND NICK AliceLife
C2 SEND USER alice 0 * :Alice Life
C2 EXPECT 001 AliceLife :*

C3 SEND PASS 1234
C3 SEND NICK BobLife
C3 SEND USER bob 0 * :Bob Life
C3 EXPECT 001 BobLife :*

# LIFE-01: Standard PING with single token
C2 SEND PING 12345
C2 EXPECT * PONG * :12345

# LIFE-02: PING with leading colon parameter
C2 SEND PING :heartbeat_token_999
C2 EXPECT * PONG * :heartbeat_token_999

# LIFE-03: PING with no parameters -> Server responds with error or handles gracefully without closing socket
C2 SEND PING
C2 EXPECT_CONNECTED

# LIFE-05: QUIT without parameter while in shared channel
C2 SEND JOIN #lifetest
C2 EXPECT :AliceLife!* JOIN #lifetest
C3 SEND JOIN #lifetest
C3 WAIT_RECV :BobLife!* JOIN #lifetest
C2 WAIT_RECV :BobLife!* JOIN #lifetest

# C2 leaves via bare QUIT
C2 SEND QUIT
C3 WAIT_RECV :AliceLife!* QUIT*
C2 EXPECT_DISCONNECT
C3 EXPECT_CONNECTED

# LIFE-06: Verify nickname AliceLife is freed and can be reclaimed by a new client
C1 RECONNECT
C1 SEND PASS 1234
C1 SEND NICK AliceLife
C1 SEND USER alice 0 * :Alice Reclaimed
C1 EXPECT 001 AliceLife :*
C1 EXPECT_CONNECTED
