# 85_KICK_self_kick_opless_channel.spec
# Tests self-kick when other members remain in the channel.
# Expected: Kicker is removed; remaining members stay in the channel without operator status (channel becomes opless).
CLIENTS C1, C2

# Alice registers and creates #lobby (op)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers and joins #lobby (regular member)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice kicks herself from #lobby
C1 SEND KICK #lobby Alice :Goodbye all
C1 EXPECT :Alice!* KICK #lobby Alice :Goodbye all
C2 EXPECT :Alice!* KICK #lobby Alice :Goodbye all

# Bob tries to set mode or kick, but is rejected because channel has no remaining ops
C2 SEND MODE #lobby +i
C2 EXPECT 482 Bob #lobby :You're not channel operator
C2 SEND KICK #lobby Alice :not op
C2 EXPECT 482 Bob #lobby :You're not channel operator
