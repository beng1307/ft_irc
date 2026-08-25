# 183_PING_empty_colon.spec
# Tests PING with empty trailing parameter (colon with no characters following)
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali269
C1 SEND USER ali269 0 * :Ali269 Smith
C1 EXPECT 001 Ali269 :*

C1 SEND PING :
C1 EXPECT :localhost PONG localhost :
