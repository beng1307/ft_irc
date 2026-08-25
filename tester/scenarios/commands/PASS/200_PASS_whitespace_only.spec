# 200_PASS_whitespace_only.spec
# PASS with trailing whitespace only must be treated as missing parameters and return 461
CLIENTS C1

C1 SEND_RAW PASS    \r\n
C1 EXPECT 461 * PASS :Not enough parameters
