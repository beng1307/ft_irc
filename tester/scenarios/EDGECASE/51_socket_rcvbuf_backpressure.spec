CLIENTS C1, C2, C3

# Register C1, C2, C3
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

# Join channel
C1 SEND JOIN #backpressure
C2 SEND JOIN #backpressure
C3 SEND JOIN #backpressure

# Shrink C1's receive window to minimum and pause reading
C1 SET_SOCK_RCVBUF 1024
C1 PAUSE

# C2 floods channel to fill C1's TCP buffer
C2 FLOOD 20 PRIVMSG #backpressure :FloodPayload_0123456789ABCDEF

# Verify C3 is still active and server loop is responsive
C3 SEND PING :alive
C3 EXPECT PONG * :alive

# Resume C1 reading
C1 RESUME
C1 EXPECT_CONNECTED
