# A kicked client cannot use the channel, but its socket and other channels remain usable.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali046
C1 SEND USER ali046 0 * :Ali046
C1 EXPECT 001 Ali046 :*

C2 SEND PASS 1234
C2 SEND NICK Bob046
C2 SEND USER bob046 0 * :Bob046
C2 EXPECT 001 Bob046 :*

C1 SEND JOIN #kick
C1 EXPECT :Ali046!* JOIN #kick
C2 SEND JOIN #kick
C2 WAIT_RECV :Bob046!* JOIN #kick
C1 WAIT_RECV :Bob046!* JOIN #kick

C1 SEND KICK #kick Bob046 :removed
C2 WAIT_RECV :Ali046!* KICK #kick Bob046 :removed
C1 WAIT_RECV :Ali046!* KICK #kick Bob046 :removed

C2 SEND PRIVMSG #kick :still here
C2 EXPECT 404 Bob046 #kick :Cannot send to channel

C2 SEND JOIN #kick
C2 WAIT_RECV :Bob046!* JOIN #kick
C1 WAIT_RECV :Bob046!* JOIN #kick
C2 EXPECT_CONNECTED
