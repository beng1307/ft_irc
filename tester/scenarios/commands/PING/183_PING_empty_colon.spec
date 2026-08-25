# 183_PING_empty_colon.spec
# Tests PING with empty trailing parameter (colon with no characters following)
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING :
C1 EXPECT :localhost PONG localhost :
