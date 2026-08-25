# 252_QUIT_cascading_multi_channel_op_destruction.spec
# Tests complex multi-channel cascading cleanup: C1 is op in #c1, op in #c2, and sole member in #solo.
CLIENTS C1, C2, C3, C4

# C1, C2, C3, C4 register
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

C4 SEND PASS 1234
C4 SEND NICK Dave
C4 SEND USER dave 0 * :Dave
C4 EXPECT 001 Dave :*

# C1 creates #c1, #c2, #solo
C1 SEND JOIN #c1
C1 EXPECT :Alice!* JOIN #c1
C2 SEND JOIN #c1
C2 WAIT_RECV :Bob!* JOIN #c1
C1 WAIT_RECV :Bob!* JOIN #c1
C3 SEND JOIN #c1
C3 WAIT_RECV :Charlie!* JOIN #c1
C1 WAIT_RECV :Charlie!* JOIN #c1

C1 SEND JOIN #c2
C1 EXPECT :Alice!* JOIN #c2
C4 SEND JOIN #c2
C4 WAIT_RECV :Dave!* JOIN #c2
C1 WAIT_RECV :Dave!* JOIN #c2

C1 SEND JOIN #solo
C1 EXPECT :Alice!* JOIN #solo

# C1 quits
C1 SEND QUIT :Mass cleanup
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob and Charlie in #c1 receive QUIT
C2 WAIT_RECV :Alice!* QUIT :Mass cleanup
C3 WAIT_RECV :Alice!* QUIT :Mass cleanup

# Dave in #c2 receives QUIT
C4 WAIT_RECV :Alice!* QUIT :Mass cleanup

# Bob was promoted to op in #c1 and can set mode
C2 SEND MODE #c1 +t
C2 EXPECT :Bob!* MODE #c1 +t

# Dave was promoted to op in #c2 and can set mode
C4 SEND MODE #c2 +i
C4 EXPECT :Dave!* MODE #c2 +i
