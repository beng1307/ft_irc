# Demonstrate indefinite wait when a client sends QUIT while backpressured and refuses to read.
# Because the kernel send buffer never drains and no drain timeout exists, the client stays connected.
CLIENTS C1, C2, C3
TIMEOUT 10s

# Register C1 (the backpressured quitting client), C2 (traffic generator), and C3 (liveness probe).
C1 SEND PASS 1234
C1 SEND NICK Ali415
C1 SEND USER ali415 0 * :Ali415
C1 EXPECT 001 Ali415 :*

C2 SEND PASS 1234
C2 SEND NICK Bob415
C2 SEND USER bob415 0 * :Bob415
C2 EXPECT 001 Bob415 :*

C3 SEND PASS 1234
C3 SEND NICK Cha415
C3 SEND USER cha415 0 * :Cha415
C3 EXPECT 001 Cha415 :*

# C1 and C2 join a channel together.
C1 SEND JOIN #quit_backpressure
C1 EXPECT :Ali415!* JOIN #quit_backpressure
C2 SEND JOIN #quit_backpressure
C2 EXPECT :Bob415!* JOIN #quit_backpressure
C1 WAIT_RECV :Bob415!* JOIN #quit_backpressure

# C1 shrinks receive window to minimum and pauses reading (simulating frozen/unresponsive client).
C1 SET_SOCK_RCVBUF 1024
C1 PAUSE

# C2 floods the channel to fill C1's kernel send buffer and queued output buffer.
C2 FLOOD 100 PRIVMSG #quit_backpressure :0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789

# C1 sends QUIT command while its socket is full.
# The server queues "ERROR :Closing connection" and defers close until output buffer drains.
C1 SEND QUIT :Goodbye

# Verify that other clients (C3) remain responsive and unaffected while C1 output buffer is pending.
C3 SEND PING :liveness_check
C3 EXPECT PONG * :liveness_check

# When C1 resumes reading and drains the output buffer, the server cleanly disconnects.
C1 RESUME
C1 EXPECT_DISCONNECT

