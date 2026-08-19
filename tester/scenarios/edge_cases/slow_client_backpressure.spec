CLIENTS C1, C2, C3

# Register C1, C2, C3
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 * :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 * :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 * :*

# C1 and C2 join #heavy_traffic
C1 SEND JOIN #heavy_traffic
C1 EXPECT :Alice!* JOIN #heavy_traffic
C2 SEND JOIN #heavy_traffic
C2 EXPECT :Bob!* JOIN #heavy_traffic
C1 WAIT_RECV :Bob!* JOIN #heavy_traffic

# C1 shrinks receive window to minimal and pauses reading
C1 SET_SOCK_RCVBUF 1024
C1 PAUSE

# C2 floods #heavy_traffic to saturate server kernel write buffer for C1
C2 FLOOD 100 PRIVMSG #heavy_traffic :0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789

# C3 verifies server event loop didn't block on C1's paused write socket
C3 SEND PING :alive
C3 EXPECT PONG * :alive

# C1 resumes reading and asserts all queued frames are received
C1 RESUME
C1 EXPECT_COUNT 100 * PRIVMSG #heavy_traffic :*
