# 73_KICK_missing_params.spec
# Tests that KICK with 0 or 1 parameter returns ERR_NEEDMOREPARAMS (461).
CLIENTS C1

# Register Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# 0 parameters
C1 SEND KICK
C1 EXPECT 461 Alice KICK :Not enough parameters

# 1 parameter only (channel without target nick)
C1 SEND KICK #lobby
C1 EXPECT 461 Alice KICK :Not enough parameters
