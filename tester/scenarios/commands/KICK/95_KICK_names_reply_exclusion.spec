# 95_KICK_names_reply_exclusion.spec
# Tests that after being kicked, the target user is excluded from subsequent 353 RPL_NAMREPLY responses.
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali150
C1 SEND USER ali150 0 * :Ali150
C1 EXPECT 001 Ali150 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali150!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob150
C2 SEND USER bob150 0 * :Bob150
C2 EXPECT 001 Bob150 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob150!* JOIN #lobby
C1 WAIT_RECV :Bob150!* JOIN #lobby

# Alice kicks Bob
C1 SEND KICK #lobby Bob150 :bye
C1 EXPECT :Ali150!* KICK #lobby Bob150 :bye
C2 EXPECT :Ali150!* KICK #lobby Bob150 :bye

# Alice queries channel names (via JOIN to self or NAMES if supported)
# Or Bob rejoins to see who is in #lobby
C1 SEND PRIVMSG #lobby :Anyone else here?
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
