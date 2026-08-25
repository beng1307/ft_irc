# 185_PING_multi_colon_preservation.spec
# Tests multi-colon payload (e.g. PING :::cookie)
# RFC Requirement: PONG must echo ':::cookie' with two leading colons in payload -> ':::cookie'
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING :::cookie
C1 EXPECT :localhost PONG localhost :::cookie
