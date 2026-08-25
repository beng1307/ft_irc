# 216_QUIT_kick_then_quit_isolation.spec
# Tests that when a user is kicked from a channel and subsequently sends QUIT, no QUIT broadcast reaches the kicked channel.
CLIENTS C1, C2

# Alice (Op) and Bob in #kickquit
C1 SEND PASS 1234
C1 SEND NICK Ali331
C1 SEND USER ali331 0 * :Ali331
C1 EXPECT 001 Ali331 :*

C2 SEND PASS 1234
C2 SEND NICK Bob331
C2 SEND USER bob331 0 * :Bob331
C2 EXPECT 001 Bob331 :*

C1 SEND JOIN #kickquit
C1 EXPECT :Ali331!* JOIN #kickquit

C2 SEND JOIN #kickquit
C2 WAIT_RECV :Bob331!* JOIN #kickquit
C1 WAIT_RECV :Bob331!* JOIN #kickquit

# Alice kicks Bob
C1 SEND KICK #kickquit Bob331 :Rule violation
C1 EXPECT :Ali331!* KICK #kickquit Bob331 :Rule violation
C2 WAIT_RECV :Ali331!* KICK #kickquit Bob331 :Rule violation

# Bob sends QUIT
C2 SEND QUIT :Leaving after kick
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECT

# Alice receives no QUIT broadcast
C1 SEND PRIVMSG #kickquit :Still intact
C1 EXPECT_CONNECTED
