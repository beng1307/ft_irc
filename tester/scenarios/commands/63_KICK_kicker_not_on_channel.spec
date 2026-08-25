# 63_KICK_kicker_not_on_channel.spec
# Tests that an operator/user attempting to KICK from outside the channel returns ERR_NOTONCHANNEL (442).
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers but does not join #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Bob tries to kick Alice from #lobby
C2 SEND KICK #lobby Alice :intruder
C2 EXPECT 442 Bob #lobby :You're not on that channel
