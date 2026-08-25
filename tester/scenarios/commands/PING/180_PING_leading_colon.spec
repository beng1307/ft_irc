# 180_PING_leading_colon.spec
# Tests PING command with single colon-prefixed token
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING :mycookie
C1 EXPECT :localhost PONG localhost :mycookie
