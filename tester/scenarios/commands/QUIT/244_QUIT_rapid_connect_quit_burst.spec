# 217_QUIT_rapid_connect_quit_burst.spec
# Tests rapid connect, join, and QUIT sequences to verify socket and memory stability.
CLIENTS C1, C2, C3

# Alice in #burst
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #burst
C1 EXPECT :Alice!* JOIN #burst

# Bob connects, joins, quits
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #burst
C2 WAIT_RECV :Bob!* JOIN #burst
C1 WAIT_RECV :Bob!* JOIN #burst

C2 SEND QUIT :Bob rapid exit
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECT
C1 WAIT_RECV :Bob!* QUIT :Bob rapid exit

# Charlie connects, joins, quits
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*
C3 SEND JOIN #burst
C3 WAIT_RECV :Charlie!* JOIN #burst
C1 WAIT_RECV :Charlie!* JOIN #burst

C3 SEND QUIT :Charlie rapid exit
C3 EXPECT ERROR :Closing connection
C3 EXPECT_DISCONNECT
C1 WAIT_RECV :Charlie!* QUIT :Charlie rapid exit

# Alice remains connected and healthy
C1 SEND PRIVMSG #burst :Server survived burst
C1 EXPECT_CONNECTED
