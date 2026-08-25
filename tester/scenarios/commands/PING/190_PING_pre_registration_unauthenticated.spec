# 190_PING_pre_registration_unauthenticated.spec
# Tests PING on raw connection before sending PASS, NICK, or USER.
# Server should reply with PONG, and allow subsequent normal registration.
CLIENTS C1

C1 SEND PING probe123
C1 EXPECT :localhost PONG localhost :probe123

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*
