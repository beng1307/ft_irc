# 85_KICK_self_kick_opless_channel.spec
# Tests self-kick when other members remain in the channel.
# Expected: Kicker is removed; remaining members stay in the channel without operator status (channel becomes opless).
CLIENTS C1, C2

# Alice registers and creates #lobby85K (op)
C1 SEND PASS 1234
C1 SEND NICK Ali140
C1 SEND USER ali140 0 * :Ali140
C1 EXPECT 001 Ali140 :*
C1 SEND JOIN #lobby85K
C1 EXPECT :Ali140!* JOIN #lobby85K

# Bob registers and joins #lobby85K (regular member)
C2 SEND PASS 1234
C2 SEND NICK Bob140
C2 SEND USER bob140 0 * :Bob140
C2 EXPECT 001 Bob140 :*
C2 SEND JOIN #lobby85K
C2 EXPECT :Bob140!* JOIN #lobby85K
C1 WAIT_RECV :Bob140!* JOIN #lobby85K

# Alice kicks herself from #lobby85K
C1 SEND KICK #lobby85K Ali140 :Goodbye all
C1 EXPECT :Ali140!* KICK #lobby85K Ali140 :Goodbye all
C2 EXPECT :Ali140!* KICK #lobby85K Ali140 :Goodbye all

# Bob tries to set mode or kick, but is rejected because channel has no remaining ops
C2 SEND MODE #lobby85K +i
C2 EXPECT 482 Bob140 #lobby85K :You're not channel operator
C2 SEND KICK #lobby85K Ali140 :not op
C2 EXPECT 482 Bob140 #lobby85K :You're not channel operator
