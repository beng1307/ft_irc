# 155_PART_audience_isolation_after_part.spec
# Tests that after parting the only mutual channel, former peers do not receive subsequent NICK changes.
CLIENTS C1, C2

# Setup: Alice and Bob in #lobby155P (only shared channel)
C1 SEND PASS 1234
C1 SEND NICK Ali224
C1 SEND USER ali224 0 * :Ali224
C1 EXPECT 001 Ali224 :*
C1 SEND JOIN #lobby155P
C1 EXPECT :Ali224!* JOIN #lobby155P

C2 SEND PASS 1234
C2 SEND NICK Bob224
C2 SEND USER bob224 0 * :Bob224
C2 EXPECT 001 Bob224 :*
C2 SEND JOIN #lobby155P
C2 EXPECT :Bob224!* JOIN #lobby155P
C1 WAIT_RECV :Bob224!* JOIN #lobby155P

# Alice parts #lobby155P
C1 SEND PART #lobby155P :Bye
C1 EXPECT :Ali224!* PART #lobby155P :Bye
C2 EXPECT :Ali224!* PART #lobby155P :Bye

# Alice changes nickname to Alicia
C1 SEND NICK Ali224
C1 EXPECT :Ali224!* NICK :Ali224

# Bob sends message to check channel state (Bob should not have received NICK change)
C2 SEND PRIVMSG #lobby155P :Anyone here?
C2 EXPECT_NONE :Ali224!* NICK :Ali224
