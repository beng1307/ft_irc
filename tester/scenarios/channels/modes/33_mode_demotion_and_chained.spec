# Tests mode modification rejection for non-ops, operator demotion (-o), non-member +o, invalid limit (+l), and chained modes.
CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali053
C1 SEND USER ali053 0 * :Ali053
C1 EXPECT 001 Ali053 :*

C2 SEND PASS 1234
C2 SEND NICK Bob053
C2 SEND USER bob053 0 * :Bob053
C2 EXPECT 001 Bob053 :*

C3 SEND PASS 1234
C3 SEND NICK Cha053
C3 SEND USER cha053 0 * :Cha053
C3 EXPECT 001 Cha053 :*

# Alice creates channel and Bob joins
C1 SEND JOIN #advancedmodes
C1 EXPECT :Ali053!* JOIN #advancedmodes
C2 SEND JOIN #advancedmodes
C2 WAIT_RECV :Bob053!* JOIN #advancedmodes
C1 WAIT_RECV :Bob053!* JOIN #advancedmodes

# MODE-02: Non-operator Bob attempts MODE modification -> 482 ERR_CHANOPRIVSNEEDED
C2 SEND MODE #advancedmodes +i
C2 EXPECT 482 Bob053 #advancedmodes :*

# MODE-11: Operator Alice attempts MODE +o on Charlie (who is not in channel)
C1 SEND MODE #advancedmodes +o Cha053
C1 EXPECT 441 Ali053 Cha053 #advancedmodes :*

# MODE-14: Invalid user limit (+l non-numeric or negative)
C1 SEND MODE #advancedmodes +l -5
C1 EXPECT_CONNECTED
C1 SEND MODE #advancedmodes +l invalidlimit
C1 EXPECT_CONNECTED

# MODE-09: Alice grants op to Bob (+o)
C1 SEND MODE #advancedmodes +o Bob053
C2 WAIT_RECV :Ali053!* MODE #advancedmodes +o Bob053
C1 WAIT_RECV :Ali053!* MODE #advancedmodes +o Bob053

# Bob (now op) can set modes
C2 SEND MODE #advancedmodes +t
C1 WAIT_RECV :Bob053!* MODE #advancedmodes +t
C2 WAIT_RECV :Bob053!* MODE #advancedmodes +t

# MODE-10: Alice revokes Bob's op status (-o)
C1 SEND MODE #advancedmodes -o Bob053
C1 WAIT_RECV :Ali053!* MODE #advancedmodes -o Bob053
C2 WAIT_RECV :Ali053!* MODE #advancedmodes -o Bob053

# Verify Bob lost op permissions (Bob cannot remove +t)
C2 SEND MODE #advancedmodes -t
C2 EXPECT 482 Bob053 #advancedmodes :*

# MODE-15: Chained mode flags
C1 SEND MODE #advancedmodes +it
C1 WAIT_RECV :Ali053!* MODE #advancedmodes*
C2 WAIT_RECV :Ali053!* MODE #advancedmodes*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
