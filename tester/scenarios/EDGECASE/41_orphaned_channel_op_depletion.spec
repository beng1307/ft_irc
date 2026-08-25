# Scenario 41: Orphaned Channel Operator Depletion
# Tests behavior when the only channel operator leaves, leaving un-opped members in an op-less channel
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali003
C1 SEND USER ali003 0 * :Ali003
C1 EXPECT 001 Ali003 :*

C2 SEND PASS 1234
C2 SEND NICK Bob003
C2 SEND USER bob003 0 * :Bob003
C2 EXPECT 001 Bob003 :*

# Alice creates channel and sets topic restriction (+t)
C1 SEND JOIN #orphaned
C1 EXPECT :Ali003!* JOIN #orphaned
C1 SEND MODE #orphaned +t
C1 EXPECT :Ali003!* MODE #orphaned +t

# Bob joins
C2 SEND JOIN #orphaned
C2 WAIT_RECV :Bob003!* JOIN #orphaned

# Alice (the sole operator) parts the channel
C1 SEND PART #orphaned :Leaving forever
C2 WAIT_RECV :Ali003!* PART #orphaned :Leaving forever

# Bob attempts to change topic (fails with 482 because Bob is not op)
C2 SEND TOPIC #orphaned :Bob003 Takes Over
C2 EXPECT 482 Bob003 #orphaned :You're not channel operator

# Bob attempts to change modes (fails with 482)
C2 SEND MODE #orphaned +i
C2 EXPECT 482 Bob003 #orphaned :You're not channel operator

# Channel still works for regular PRIVMSG
C2 SEND PRIVMSG #orphaned :Still here
C2 EXPECT_CONNECTED
