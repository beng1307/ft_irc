# 73_KICK_missing_params.spec
# Tests that KICK with 0 or 1 parameter returns ERR_NEEDMOREPARAMS (461).
CLIENTS C1

# Register Alice
C1 SEND PASS 1234
C1 SEND NICK Ali128
C1 SEND USER ali128 0 * :Ali128
C1 EXPECT 001 Ali128 :*

# 0 parameters
C1 SEND KICK
C1 EXPECT 461 Ali128 KICK :Not enough parameters

# 1 parameter only (channel without target nick)
C1 SEND KICK #lobby73K
C1 EXPECT 461 Ali128 KICK :Not enough parameters
