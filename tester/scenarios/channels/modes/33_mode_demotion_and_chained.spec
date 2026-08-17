# Tests mode modification rejection for non-ops, operator demotion (-o), non-member +o, invalid limit (+l), and chained modes.
CLIENTS C1, C2, C3

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

# Alice creates channel and Bob joins
C1 SEND JOIN #advancedmodes
C1 EXPECT :Alice!* JOIN #advancedmodes
C2 SEND JOIN #advancedmodes
C2 WAIT_RECV :Bob!* JOIN #advancedmodes
C1 WAIT_RECV :Bob!* JOIN #advancedmodes

# MODE-02: Non-operator Bob attempts MODE modification -> 482 ERR_CHANOPRIVSNEEDED
C2 SEND MODE #advancedmodes +i
C2 EXPECT 482 Bob #advancedmodes :*

# MODE-11: Operator Alice attempts MODE +o on Charlie (who is not in channel)
C1 SEND MODE #advancedmodes +o Charlie
C1 EXPECT 441 Alice Charlie #advancedmodes :*

# MODE-14: Invalid user limit (+l non-numeric or negative)
C1 SEND MODE #advancedmodes +l -5
C1 EXPECT_CONNECTED
C1 SEND MODE #advancedmodes +l invalidlimit
C1 EXPECT_CONNECTED

# MODE-09: Alice grants op to Bob (+o)
C1 SEND MODE #advancedmodes +o Bob
C2 WAIT_RECV :Alice!* MODE #advancedmodes +o Bob
C1 WAIT_RECV :Alice!* MODE #advancedmodes +o Bob

# Bob (now op) can set modes
C2 SEND MODE #advancedmodes +t
C1 WAIT_RECV :Bob!* MODE #advancedmodes +t
C2 WAIT_RECV :Bob!* MODE #advancedmodes +t

# MODE-10: Alice revokes Bob's op status (-o)
C1 SEND MODE #advancedmodes -o Bob
C1 WAIT_RECV :Alice!* MODE #advancedmodes -o Bob
C2 WAIT_RECV :Alice!* MODE #advancedmodes -o Bob

# Verify Bob lost op permissions (Bob cannot remove +t)
C2 SEND MODE #advancedmodes -t
C2 EXPECT 482 Bob #advancedmodes :*

# MODE-15: Chained mode flags
C1 SEND MODE #advancedmodes +it
C1 WAIT_RECV :Alice!* MODE #advancedmodes*
C2 WAIT_RECV :Alice!* MODE #advancedmodes*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
