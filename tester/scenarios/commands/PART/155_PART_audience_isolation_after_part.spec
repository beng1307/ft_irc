# 155_PART_audience_isolation_after_part.spec
# Tests that after parting the only mutual channel, former peers do not receive subsequent NICK changes.
CLIENTS C1, C2

# Setup: Alice and Bob in #lobby (only shared channel)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice parts #lobby
C1 SEND PART #lobby :Bye
C1 EXPECT :Alice!* PART #lobby :Bye
C2 EXPECT :Alice!* PART #lobby :Bye

# Alice changes nickname to Alicia
C1 SEND NICK Alicia
C1 EXPECT :Alice!* NICK :Alicia

# Bob sends message to check channel state (Bob should not have received NICK change)
C2 SEND PRIVMSG #lobby :Anyone here?
C2 EXPECT_NONE :Alice!* NICK :Alicia
