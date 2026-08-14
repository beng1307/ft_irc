# A kicked client cannot use the channel, but its socket and other channels remain usable.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #kick
C1 EXPECT :Alice!* JOIN #kick
C2 SEND JOIN #kick
C2 WAIT_RECV :Bob!* JOIN #kick
C1 WAIT_RECV :Bob!* JOIN #kick

C1 SEND KICK #kick Bob :removed
C2 WAIT_RECV :Alice!* KICK #kick Bob :removed
C1 WAIT_RECV :Alice!* KICK #kick Bob :removed

C2 SEND PRIVMSG #kick :still here
C2 EXPECT 442 Bob #kick :You're not on that channel

C2 SEND JOIN #kick
C2 WAIT_RECV :Bob!* JOIN #kick
C1 WAIT_RECV :Bob!* JOIN #kick
C2 EXPECT_CONNECTED
