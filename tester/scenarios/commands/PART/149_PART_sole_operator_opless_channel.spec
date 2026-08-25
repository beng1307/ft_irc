# 149_PART_sole_operator_opless_channel.spec
# Tests that when the only channel operator parts, remaining members remain in an opless channel
# and cannot perform operator actions (e.g. MODE).
CLIENTS C1, C2

# Setup: Alice (op) and Bob (regular member) in #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice (the sole operator) parts
C1 SEND PART #lobby :Leaving
C1 EXPECT :Alice!* PART #lobby :Leaving
C2 EXPECT :Alice!* PART #lobby :Leaving

# Bob attempts to set mode +i (should fail with 482 because channel has no ops)
C2 SEND MODE #lobby +i
C2 EXPECT 482 Bob #lobby :You're not channel operator
