# 118_PART_reason_with_colon.spec
# Tests RFC 2812 §3.2.2 standard PART command with colon reason
# Expected: Server broadcasts ':Alice!* PART #lobby :Going to sleep' to both Alice and Bob.
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

# Alice parts with colon reason
C1 SEND PART #lobby :Going to sleep
C1 EXPECT :Alice!* PART #lobby :Going to sleep
C2 EXPECT :Alice!* PART #lobby :Going to sleep
