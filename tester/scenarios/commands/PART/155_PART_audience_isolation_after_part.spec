# 155_PART_audience_isolation_after_part.spec
# Tests that after parting the only mutual channel, former peers do not receive subsequent NICK changes.
CLIENTS C1, C2

# Setup: Alice and Bob in #lobby (only shared channel)
C1 SEND PASS 1234
C1 SEND NICK Ali224
C1 SEND USER ali224 0 * :Ali224
C1 EXPECT 001 Ali224 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali224!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob224
C2 SEND USER bob224 0 * :Bob224
C2 EXPECT 001 Bob224 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob224!* JOIN #lobby
C1 WAIT_RECV :Bob224!* JOIN #lobby

# Alice parts #lobby
C1 SEND PART #lobby :Bye
C1 EXPECT :Ali224!* PART #lobby :Bye
C2 EXPECT :Ali224!* PART #lobby :Bye

# Alice changes nickname to Alicia
C1 SEND NICK Ali224
C1 EXPECT :Ali224!* NICK :Ali224

# Bob sends message to check channel state (Bob should not have received NICK change)
C2 SEND PRIVMSG #lobby :Anyone here?
C2 EXPECT_NONE :Ali224!* NICK :Ali224
