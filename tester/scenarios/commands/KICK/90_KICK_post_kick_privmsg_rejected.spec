# 90_KICK_post_kick_privmsg_rejected.spec
# Tests that a kicked user's subsequent channel messages are rejected with ERR_NOTONCHANNEL (442).
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali145
C1 SEND USER ali145 0 * :Ali145
C1 EXPECT 001 Ali145 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali145!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob145
C2 SEND USER bob145 0 * :Bob145
C2 EXPECT 001 Bob145 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob145!* JOIN #lobby
C1 WAIT_RECV :Bob145!* JOIN #lobby

# Alice kicks Bob
C1 SEND KICK #lobby Bob145 :banned from talking
C1 EXPECT :Ali145!* KICK #lobby Bob145 :banned from talking
C2 EXPECT :Ali145!* KICK #lobby Bob145 :banned from talking

# Bob attempts to send PRIVMSG to #lobby
C2 SEND PRIVMSG #lobby :Can anyone hear me?
C2 EXPECT 404 Bob145 #lobby :Cannot send to channel

