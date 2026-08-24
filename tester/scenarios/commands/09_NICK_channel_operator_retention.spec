# 09_NICK_channel_operator_retention.spec
# Tests that channel operator privileges (+o) and invite states persist across nickname changes.
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C1 creates channel #ops and becomes operator
C1 SEND JOIN #ops
C1 EXPECT :Alice!* JOIN #ops

# C1 changes nickname to SuperAlice
C1 SEND NICK SuperAlice
C1 WAIT_RECV :Alice!* NICK :SuperAlice

# C2 registers as Bob and joins #ops
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #ops
C1 WAIT_RECV :Bob!* JOIN #ops

# C1 kicks Bob from channel using operator privilege
C1 SEND KICK #ops Bob :Operator privilege maintained
C2 WAIT_RECV :SuperAlice!* KICK #ops Bob :Operator privilege maintained
C2 EXPECT_CONNECTED
