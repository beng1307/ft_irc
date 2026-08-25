# 149_PART_sole_operator_opless_channel.spec
# Tests that when the only channel operator parts, remaining members remain in an opless channel
# and cannot perform operator actions (e.g. MODE).
CLIENTS C1, C2

# Setup: Alice (op) and Bob (regular member) in #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali218
C1 SEND USER ali218 0 * :Ali218
C1 EXPECT 001 Ali218 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali218!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob218
C2 SEND USER bob218 0 * :Bob218
C2 EXPECT 001 Bob218 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob218!* JOIN #lobby
C1 WAIT_RECV :Bob218!* JOIN #lobby

# Alice (the sole operator) parts
C1 SEND PART #lobby :Leaving
C1 EXPECT :Ali218!* PART #lobby :Leaving
C2 EXPECT :Ali218!* PART #lobby :Leaving

# Bob attempts to set mode +i (should fail with 482 because channel has no ops)
C2 SEND MODE #lobby +i
C2 EXPECT 482 Bob218 #lobby :You're not channel operator
