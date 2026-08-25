# 217_QUIT_rapid_connect_quit_burst.spec
# Tests rapid connect, join, and QUIT sequences to verify socket and memory stability.
CLIENTS C1, C2, C3

# Alice in #burst
C1 SEND PASS 1234
C1 SEND NICK Ali332
C1 SEND USER ali332 0 * :Ali332
C1 EXPECT 001 Ali332 :*
C1 SEND JOIN #burst
C1 EXPECT :Ali332!* JOIN #burst

# Bob connects, joins, quits
C2 SEND PASS 1234
C2 SEND NICK Bob332
C2 SEND USER bob332 0 * :Bob332
C2 EXPECT 001 Bob332 :*
C2 SEND JOIN #burst
C2 WAIT_RECV :Bob332!* JOIN #burst
C1 WAIT_RECV :Bob332!* JOIN #burst

C2 SEND QUIT :Bob332 rapid exit
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECT
C1 WAIT_RECV :Bob332!* QUIT :Bob332 rapid exit

# Charlie connects, joins, quits
C3 SEND PASS 1234
C3 SEND NICK Cha332
C3 SEND USER cha332 0 * :Cha332
C3 EXPECT 001 Cha332 :*
C3 SEND JOIN #burst
C3 WAIT_RECV :Cha332!* JOIN #burst
C1 WAIT_RECV :Cha332!* JOIN #burst

C3 SEND QUIT :Cha332 rapid exit
C3 EXPECT ERROR :Closing connection
C3 EXPECT_DISCONNECT
C1 WAIT_RECV :Cha332!* QUIT :Cha332 rapid exit

# Alice remains connected and healthy
C1 SEND PRIVMSG #burst :Server survived burst
C1 EXPECT_CONNECTED
