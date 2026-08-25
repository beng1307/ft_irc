# 75_KICK_kicker_not_on_channel.spec
# Tests that an operator/user attempting to KICK from outside the channel returns ERR_NOTONCHANNEL (442).
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali130
C1 SEND USER ali130 0 * :Ali130
C1 EXPECT 001 Ali130 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali130!* JOIN #lobby

# Bob registers but does not join #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob130
C2 SEND USER bob130 0 * :Bob130
C2 EXPECT 001 Bob130 :*

# Bob tries to kick Alice from #lobby
C2 SEND KICK #lobby Ali130 :intruder
C2 EXPECT 442 Bob130 #lobby :You're not on that channel
