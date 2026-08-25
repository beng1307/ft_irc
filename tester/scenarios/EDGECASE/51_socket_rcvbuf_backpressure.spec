CLIENTS C1, C2, C3

# Register C1, C2, C3
C1 SEND PASS 1234
C1 SEND NICK Ali013
C1 SEND USER ali013 0 * :Ali013
C1 EXPECT 001 Ali013 :*

C2 SEND PASS 1234
C2 SEND NICK Bob013
C2 SEND USER bob013 0 * :Bob013
C2 EXPECT 001 Bob013 :*

C3 SEND PASS 1234
C3 SEND NICK Cha013
C3 SEND USER cha013 0 * :Cha013
C3 EXPECT 001 Cha013 :*

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
