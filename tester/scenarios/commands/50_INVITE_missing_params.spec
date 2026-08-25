# 50_INVITE_missing_params.spec
# Tests INVITE command with missing parameters (< 2 parameters).
# Expected: Server rejects with 461 ERR_NEEDMOREPARAMS.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice50
C1 SEND USER alice50 0 * :Alice
C1 EXPECT 001 Alice50 :*

# No parameters
C1 SEND INVITE
C1 EXPECT 461 Alice50 INVITE :Not enough parameters

# Single parameter (target only)
C1 SEND INVITE Bob50
C1 EXPECT 461 Alice50 INVITE :Not enough parameters
C1 EXPECT_CONNECTED
