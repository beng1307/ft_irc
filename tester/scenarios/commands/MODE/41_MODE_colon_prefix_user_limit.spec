# 41_MODE_colon_prefix_user_limit.spec
# Tests setting channel user limit with colon prefix (e.g. MODE #chan +l :10)
# Expected: Server parses ":10" as integer limit 10 and broadcasts MODE #chan +l 10.
# Bug: Server fails is_positive_number(":10") and rejects with 461 MODE :Not enough parameters.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali158
C1 SEND USER ali158 0 * :Ali158
C1 EXPECT 001 Ali158 :*

C1 SEND JOIN #chan
C1 EXPECT 353 Ali158 = #chan :@Ali158
C1 EXPECT 366 Ali158 #chan :End of /NAMES list

# Set limit with colon prefix
C1 SEND MODE #chan +l :10
C1 EXPECT :Ali158!* MODE #chan +l 10
