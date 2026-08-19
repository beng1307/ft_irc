# Scenario 41: Orphaned Channel Operator Depletion
# Tests behavior when the only channel operator leaves, leaving un-opped members in an op-less channel
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates channel and sets topic restriction (+t)
C1 SEND JOIN #orphaned
C1 EXPECT :Alice!* JOIN #orphaned
C1 SEND MODE #orphaned +t
C1 EXPECT :Alice!* MODE #orphaned +t

# Bob joins
C2 SEND JOIN #orphaned
C2 WAIT_RECV :Bob!* JOIN #orphaned

# Alice (the sole operator) parts the channel
C1 SEND PART #orphaned :Leaving forever
C2 WAIT_RECV :Alice!* PART #orphaned :Leaving forever

# Bob attempts to change topic (fails with 482 because Bob is not op)
C2 SEND TOPIC #orphaned :Bob Takes Over
C2 EXPECT 482 Bob #orphaned :You're not channel operator

# Bob attempts to change modes (fails with 482)
C2 SEND MODE #orphaned +i
C2 EXPECT 482 Bob #orphaned :You're not channel operator

# Channel still works for regular PRIVMSG
C2 SEND PRIVMSG #orphaned :Still here
C2 EXPECT_CONNECTED
