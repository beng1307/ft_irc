# 78_KICK_target_not_on_channel.spec
# Tests that an operator attempting to KICK a registered user who is NOT in the channel returns ERR_USERNOTINCHANNEL (441).
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

# Alice attempts to kick Bob from #lobby
C1 SEND KICK #lobby Bob :not here
C1 EXPECT 441 Alice Bob #lobby :They aren't on that channel
