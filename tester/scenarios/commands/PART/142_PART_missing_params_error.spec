# 142_PART_missing_params_error.spec
# Tests ERR_NEEDMOREPARAMS (461) when PART is issued without channel parameter
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali211
C1 SEND USER ali211 0 * :Ali211
C1 EXPECT 001 Ali211 :*

# PART with no arguments
C1 SEND PART
C1 EXPECT 461 Ali211 PART :Not enough parameters

# PART with whitespace only
C1 SEND PART   
C1 EXPECT 461 Ali211 PART :Not enough parameters
