# Demonstrate indefinite wait when a client sends QUIT while backpressured and refuses to read.
# Because the kernel send buffer never drains and no drain timeout exists, the client stays connected.
CLIENTS C1, C2, C3
TIMEOUT 10s

# Register C1 (the backpressured quitting client), C2 (traffic generator), and C3 (liveness probe).
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# C1 and C2 join a channel together.
C1 SEND JOIN #quit_backpressure
C1 EXPECT :Alice!* JOIN #quit_backpressure
C2 SEND JOIN #quit_backpressure
C2 EXPECT :Bob!* JOIN #quit_backpressure
C1 WAIT_RECV :Bob!* JOIN #quit_backpressure

# C1 shrinks receive window to minimum and pauses reading (simulating frozen/unresponsive client).
C1 SET_SOCK_RCVBUF 1024
C1 PAUSE

# C2 floods the channel to fill C1's kernel send buffer and queued output buffer.
C2 FLOOD 100 PRIVMSG #quit_backpressure :0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789

# C1 sends QUIT command while its socket is full.
# The server queues "ERROR :Closing connection" and sets close_after_output = true,
# but cannot flush the buffer because C1 is not reading.
C1 SEND QUIT :Goodbye

# Wait a period of time to verify C1 does NOT get disconnected while unresponsive.
WAIT 5s

# C1's connection remains open on the server (indefinite wait due to lack of drain timeout).
C1 EXPECT_DISCONNECT

# Verify that other clients (C3) remain responsive and unaffected.
C3 SEND PING :liveness_check
C3 EXPECT PONG * :liveness_check

# When C1 finally resumes reading and drains the output buffer:
C1 RESUME

# The server finishes flushing and cleanly closes the connection upon seeing an empty output buffer.
C1 EXPECT_DISCONNECT
