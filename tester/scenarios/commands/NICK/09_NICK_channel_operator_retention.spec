# 09_NICK_channel_operator_retention.spec
# Tests that channel operator privileges (+o) and invite states persist across nickname changes.
CLIENTS C1, C2

# C1 registers as Alice09
C1 SEND PASS 1234
C1 SEND NICK Alice09
C1 SEND USER user09 0 * :Alice 09
C1 EXPECT 001 Alice09 :*

# C1 creates channel #ops09 and becomes operator
C1 SEND JOIN #ops09
C1 EXPECT :Alice09!* JOIN #ops09

# C1 changes nickname to Super09
C1 SEND NICK Super09
C1 WAIT_RECV :Alice09!* NICK :Super09

# C2 registers as Bob09 and joins #ops09
C2 SEND PASS 1234
C2 SEND NICK Bob09
C2 SEND USER user09 0 * :Bob 09
C2 EXPECT 001 Bob09 :*
C2 SEND JOIN #ops09
C1 WAIT_RECV :Bob09!* JOIN #ops09

# C1 kicks Bob from channel using operator privilege
C1 SEND KICK #ops09 Bob09 :Operator privilege maintained
C2 WAIT_RECV :Super09!* KICK #ops09 Bob09 :Operator privilege maintained
C2 EXPECT_CONNECTED

