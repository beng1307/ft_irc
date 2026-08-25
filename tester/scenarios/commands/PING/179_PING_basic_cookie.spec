# 179_PING_basic_cookie.spec
# Tests standard PING command with single alphanumeric cookie argument
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING 123456
C1 EXPECT :localhost PONG localhost :123456
