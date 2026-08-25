# 141_PART_single_word_reason_without_colon.spec
# Tests RFC 2812 §3.2.2 single-word part reason without leading colon: PART #lobby Goodbye
# Expected: Server extracts 'Goodbye' as part reason and broadcasts ':Alice!* PART #lobby :Goodbye'.
# Bug: Server strictly checks for ' :' (line.contains(" :")), failing when no colon is supplied and discarding the reason.
CLIENTS C1, C2

# Setup: Alice and Bob join #lobby
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

# Alice parts with single-word reason 'Goodbye' (no colon)
C1 SEND PART #lobby Goodbye
C1 EXPECT :Alice!* PART #lobby :Goodbye
C2 EXPECT :Alice!* PART #lobby :Goodbye
