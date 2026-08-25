# 141_PART_single_word_reason_without_colon.spec
# Tests RFC 2812 §3.2.2 single-word part reason without leading colon: PART #lobby Goodbye
# Expected: Server extracts 'Goodbye' as part reason and broadcasts ':Alice!* PART #lobby :Goodbye'.
# Bug: Server strictly checks for ' :' (line.contains(" :")), failing when no colon is supplied and discarding the reason.
CLIENTS C1, C2

# Setup: Alice and Bob join #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali210
C1 SEND USER ali210 0 * :Ali210
C1 EXPECT 001 Ali210 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali210!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob210
C2 SEND USER bob210 0 * :Bob210
C2 EXPECT 001 Bob210 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob210!* JOIN #lobby
C1 WAIT_RECV :Bob210!* JOIN #lobby

# Alice parts with single-word reason 'Goodbye' (no colon)
C1 SEND PART #lobby Goodbye
C1 EXPECT :Ali210!* PART #lobby :Goodbye
C2 EXPECT :Ali210!* PART #lobby :Goodbye
