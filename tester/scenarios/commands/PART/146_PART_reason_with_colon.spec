# 146_PART_reason_with_colon.spec
# Tests RFC 2812 §3.2.2 standard PART command with colon reason
# Expected: Server broadcasts ':Alice!* PART #lobby :Going to sleep' to both Alice and Bob.
CLIENTS C1, C2

# Setup: Alice and Bob in #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali215
C1 SEND USER ali215 0 * :Ali215
C1 EXPECT 001 Ali215 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali215!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob215
C2 SEND USER bob215 0 * :Bob215
C2 EXPECT 001 Bob215 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob215!* JOIN #lobby
C1 WAIT_RECV :Bob215!* JOIN #lobby

# Alice parts with colon reason
C1 SEND PART #lobby :Going to sleep
C1 EXPECT :Ali215!* PART #lobby :Going to sleep
C2 EXPECT :Ali215!* PART #lobby :Going to sleep
