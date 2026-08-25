# 156_PART_internal_colons_reason.spec
# Tests that part reasons with multiple internal colons are preserved in full.
CLIENTS C1, C2

# Setup: Alice and Bob in #lobby
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

# Alice parts with colons in reason
C1 SEND PART #lobby :leaving: reason:with:colons
C1 EXPECT :Alice!* PART #lobby :leaving: reason:with:colons
C2 EXPECT :Alice!* PART #lobby :leaving: reason:with:colons
