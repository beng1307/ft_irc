# 153_PART_post_part_privmsg_blocked.spec
# Tests that messages sent to a channel after parting are blocked with 442 ERR_NOTONCHANNEL.
CLIENTS C1, C2

# Setup: Alice and Bob join #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali222
C1 SEND USER ali222 0 * :Ali222
C1 EXPECT 001 Ali222 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali222!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob222
C2 SEND USER bob222 0 * :Bob222
C2 EXPECT 001 Bob222 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob222!* JOIN #lobby
C1 WAIT_RECV :Bob222!* JOIN #lobby

# Alice parts #lobby
C1 SEND PART #lobby :Bye
C1 EXPECT :Ali222!* PART #lobby :Bye
C2 EXPECT :Ali222!* PART #lobby :Bye

# Alice tries to send PRIVMSG to #lobby
C1 SEND PRIVMSG #lobby :Can you hear me?
C1 EXPECT 404 Ali222 #lobby :Cannot send to channel

