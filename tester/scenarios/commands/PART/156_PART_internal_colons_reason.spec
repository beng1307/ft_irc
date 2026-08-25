# 156_PART_internal_colons_reason.spec
# Tests that part reasons with multiple internal colons are preserved in full.
CLIENTS C1, C2

# Setup: Alice and Bob in #lobby156P
C1 SEND PASS 1234
C1 SEND NICK Ali225
C1 SEND USER ali225 0 * :Ali225
C1 EXPECT 001 Ali225 :*
C1 SEND JOIN #lobby156P
C1 EXPECT :Ali225!* JOIN #lobby156P

C2 SEND PASS 1234
C2 SEND NICK Bob225
C2 SEND USER bob225 0 * :Bob225
C2 EXPECT 001 Bob225 :*
C2 SEND JOIN #lobby156P
C2 EXPECT :Bob225!* JOIN #lobby156P
C1 WAIT_RECV :Bob225!* JOIN #lobby156P

# Alice parts with colons in reason
C1 SEND PART #lobby156P :leaving: reason:with:colons
C1 EXPECT :Ali225!* PART #lobby156P :leaving: reason:with:colons
C2 EXPECT :Ali225!* PART #lobby156P :leaving: reason:with:colons
