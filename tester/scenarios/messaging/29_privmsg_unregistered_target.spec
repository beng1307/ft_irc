# PRIVMSG to unregistered client (before PASS/NICK/USER complete).
# Should fail gracefully - sender should get error or disconnect.

CLIENTS C1, C2

# C1 fully registers
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 connects but doesn't register fully
C2 SEND PASS 1234
C2 SEND NICK Bob
# C2 doesn't send USER yet - remains unregistered

# C1 tries to send PRIVMSG to unregistered Bob
# Server should reject because Bob is not fully registered
C1 SEND PRIVMSG Bob :Hello unregistered
C1 EXPECT 401 Alice Bob :No such nick/channel

# C2 completes registration
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Now PRIVMSG should work
C1 SEND PRIVMSG Bob :Hello registered Bob
C2 WAIT_RECV :Alice!* PRIVMSG Bob :Hello registered Bob

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
