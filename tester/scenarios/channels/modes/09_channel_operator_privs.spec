CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali050
C1 SEND USER ali050 0 * :Ali050
C1 EXPECT 001 Ali050 :*

C2 SEND PASS 1234
C2 SEND NICK Bob050
C2 SEND USER bob050 0 * :Bob050
C2 EXPECT 001 Bob050 :*

C3 SEND PASS 1234
C3 SEND NICK Cha050
C3 SEND USER cha050 0 * :Cha050
C3 EXPECT 001 Cha050 :*

C1 SEND JOIN #opchan
C1 EXPECT :Ali050!* JOIN #opchan
C2 SEND JOIN #opchan
C2 WAIT_RECV :Bob050!* JOIN #opchan
C1 WAIT_RECV :Bob050!* JOIN #opchan
C3 SEND JOIN #opchan
C3 WAIT_RECV :Cha050!* JOIN #opchan
C1 WAIT_RECV :Cha050!* JOIN #opchan

# C2 is a regular user and must receive the operator error.
C2 SEND KICK #opchan Cha050 :Out!
C2 EXPECT 482 Bob050 #opchan :You're not channel operator

# C1 grants op to C2
C1 SEND MODE #opchan +o Bob050
C1 WAIT_RECV :Ali050!* MODE #opchan +o Bob050
C2 WAIT_RECV :Ali050!* MODE #opchan +o Bob050

# Now C2 has op and can kick C3
C2 SEND KICK #opchan Cha050 :Out!
C2 WAIT_RECV :Bob050!* KICK #opchan Cha050 :Out!
C3 WAIT_RECV :Bob050!* KICK #opchan Cha050 :Out!
