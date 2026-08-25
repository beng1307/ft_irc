# 78_KICK_post_kick_privmsg_rejected.spec
# Tests that a kicked user's subsequent channel messages are rejected with ERR_NOTONCHANNEL (442).
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
C1 SEND KICK #lobby Bob :banned from talking
C1 EXPECT :Alice!* KICK #lobby Bob :banned from talking
C2 EXPECT :Alice!* KICK #lobby Bob :banned from talking

# Bob attempts to send PRIVMSG to #lobby
C2 SEND PRIVMSG #lobby :Can anyone hear me?
C2 EXPECT 442 Bob #lobby :You're not on that channel
