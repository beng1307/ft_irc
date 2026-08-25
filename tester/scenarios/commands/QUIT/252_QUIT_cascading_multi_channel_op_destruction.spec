# 252_QUIT_cascading_multi_channel_op_destruction.spec
# Tests complex multi-channel cascading cleanup: C1 is op in #c1, op in #c2, and sole member in #solo.
CLIENTS C1, C2, C3, C4

# C1, C2, C3, C4 register
C1 SEND PASS 1234
C1 SEND NICK Ali252
C1 SEND USER ali252 0 * :Ali252
C1 EXPECT 001 Ali252 :*

C2 SEND PASS 1234
C2 SEND NICK Bob340
C2 SEND USER bob340 0 * :Bob340
C2 EXPECT 001 Bob340 :*

C3 SEND PASS 1234
C3 SEND NICK Cha252
C3 SEND USER cha252 0 * :Cha252
C3 EXPECT 001 Cha252 :*

C4 SEND PASS 1234
C4 SEND NICK Dav252
C4 SEND USER dav252 0 * :Dav252
C4 EXPECT 001 Dav252 :*

# C1 creates #c1, #c2, #solo
C1 SEND JOIN #c1
C1 EXPECT :Ali252!* JOIN #c1
C2 SEND JOIN #c1
C2 WAIT_RECV :Bob340!* JOIN #c1
C1 WAIT_RECV :Bob340!* JOIN #c1
C3 SEND JOIN #c1
C3 WAIT_RECV :Cha252!* JOIN #c1
C1 WAIT_RECV :Cha252!* JOIN #c1

C1 SEND JOIN #c2
C1 EXPECT :Ali252!* JOIN #c2
C4 SEND JOIN #c2
C4 WAIT_RECV :Dav252!* JOIN #c2
C1 WAIT_RECV :Dav252!* JOIN #c2

C1 SEND JOIN #solo
C1 EXPECT :Ali252!* JOIN #solo

# C1 quits
C1 SEND QUIT :Mass cleanup
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob252 and Cha252 in #c1 receive QUIT
C2 WAIT_RECV :Ali252!* QUIT :Mass cleanup
C3 WAIT_RECV :Ali252!* QUIT :Mass cleanup

# Dav252 in #c2 receives QUIT
C4 WAIT_RECV :Ali252!* QUIT :Mass cleanup

# Bob252 was promoted to op in #c1 and can set mode
C2 SEND MODE #c1 +t
C2 EXPECT :Bob340!* MODE #c1 +t

# Dav252 was promoted to op in #c2 and can set mode
C4 SEND MODE #c2 +i
C4 EXPECT :Dav252!* MODE #c2 +i
