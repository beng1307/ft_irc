# 95_KICK_names_reply_exclusion.spec
# Tests that after being kicked, the target user is excluded from subsequent 353 RPL_NAMREPLY responses.
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice kicks Bob
C1 SEND KICK #lobby Bob :bye
C1 EXPECT :Alice!* KICK #lobby Bob :bye
C2 EXPECT :Alice!* KICK #lobby Bob :bye

# Alice queries channel names (via JOIN to self or NAMES if supported)
# Or Bob rejoins to see who is in #lobby
C1 SEND PRIVMSG #lobby :Anyone else here?
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
