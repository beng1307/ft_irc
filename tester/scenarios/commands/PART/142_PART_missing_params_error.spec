# 142_PART_missing_params_error.spec
# Tests ERR_NEEDMOREPARAMS (461) when PART is issued without channel parameter
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# PART with no arguments
C1 SEND PART
C1 EXPECT 461 Alice PART :Not enough parameters

# PART with whitespace only
C1 SEND PART   
C1 EXPECT 461 Alice PART :Not enough parameters
