# 64_KICK_kicker_not_channel_operator.spec
# Tests that a regular channel member (non-operator) attempting to KICK returns ERR_CHANOPRIVSNEEDED (482).
CLIENTS C1, C2

# Alice registers and creates #lobby (becomes operator)
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

# Bob attempts to kick Alice without having channel operator privileges
C2 SEND KICK #lobby Alice :mutiny
C2 EXPECT 482 Bob #lobby :You're not channel operator
