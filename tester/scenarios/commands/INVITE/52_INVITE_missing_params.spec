# 52_INVITE_missing_params.spec
# Tests INVITE command with missing parameters (< 2 parameters).
# Expected: Server rejects with 461 ERR_NEEDMOREPARAMS.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali077
C1 SEND USER ali077 0 * :Ali077
C1 EXPECT 001 Ali077 :*

# No parameters
C1 SEND INVITE
C1 EXPECT 461 Ali077 INVITE :Not enough parameters

# Single parameter (target only)
C1 SEND INVITE Bob077
C1 EXPECT 461 Ali077 INVITE :Not enough parameters
C1 EXPECT_CONNECTED
