# 147_PART_empty_colon_reason.spec
# Tests RFC 2812 §3.2.2 PART with empty colon parameter: PART #lobby147P :
# Expected: Server broadcasts ':Alice!* PART #lobby147P' without trailing empty parameter.
CLIENTS C1, C2

# Setup: Alice and Bob in #lobby147P
C1 SEND PASS 1234
C1 SEND NICK Ali216
C1 SEND USER ali216 0 * :Ali216
C1 EXPECT 001 Ali216 :*
C1 SEND JOIN #lobby147P
C1 EXPECT :Ali216!* JOIN #lobby147P

C2 SEND PASS 1234
C2 SEND NICK Bob216
C2 SEND USER bob216 0 * :Bob216
C2 EXPECT 001 Bob216 :*
C2 SEND JOIN #lobby147P
C2 EXPECT :Bob216!* JOIN #lobby147P
C1 WAIT_RECV :Bob216!* JOIN #lobby147P

# Alice parts with empty colon
C1 SEND PART #lobby147P :
C1 EXPECT :Ali216!* PART #lobby147P
C2 EXPECT :Ali216!* PART #lobby147P
