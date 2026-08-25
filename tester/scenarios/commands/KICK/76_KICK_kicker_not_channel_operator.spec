# 76_KICK_kicker_not_channel_operator.spec
# Tests that a regular channel member (non-operator) attempting to KICK returns ERR_CHANOPRIVSNEEDED (482).
CLIENTS C1, C2

# Alice registers and creates #lobby76K (becomes operator)
C1 SEND PASS 1234
C1 SEND NICK Ali131
C1 SEND USER ali131 0 * :Ali131
C1 EXPECT 001 Ali131 :*
C1 SEND JOIN #lobby76K
C1 EXPECT :Ali131!* JOIN #lobby76K

# Bob registers and joins #lobby76K (regular member)
C2 SEND PASS 1234
C2 SEND NICK Bob131
C2 SEND USER bob131 0 * :Bob131
C2 EXPECT 001 Bob131 :*
C2 SEND JOIN #lobby76K
C2 EXPECT :Bob131!* JOIN #lobby76K

# Bob attempts to kick Alice without having channel operator privileges
C2 SEND KICK #lobby76K Ali131 :mutiny
C2 EXPECT 482 Bob131 #lobby76K :You're not channel operator
