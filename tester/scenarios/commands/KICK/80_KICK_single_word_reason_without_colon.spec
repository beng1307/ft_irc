# 80_KICK_single_word_reason_without_colon.spec
# Tests RFC 2812 §3.2.8 single-word comment without leading colon.
# Expected: Server extracts 'spammer' as the kick comment and broadcasts ':Alice!* KICK #lobby80K Bob :spammer'.
# Bug: Server strictly checks for ' :' (line.contains(" :")), failing when no colon is supplied and silently replacing the reason with the kicker's own nickname.
CLIENTS C1, C2

# Alice registers and creates #lobby80K
C1 SEND PASS 1234
C1 SEND NICK Ali135
C1 SEND USER ali135 0 * :Ali135
C1 EXPECT 001 Ali135 :*
C1 SEND JOIN #lobby80K
C1 EXPECT :Ali135!* JOIN #lobby80K

# Bob registers and joins #lobby80K
C2 SEND PASS 1234
C2 SEND NICK Bob135
C2 SEND USER bob135 0 * :Bob135
C2 EXPECT 001 Bob135 :*
C2 SEND JOIN #lobby80K
C2 EXPECT :Bob135!* JOIN #lobby80K
C1 WAIT_RECV :Bob135!* JOIN #lobby80K

# Alice kicks Bob with single-word reason 'spammer' (no colon)
C1 SEND KICK #lobby80K Bob135 spammer
C1 EXPECT :Ali135!* KICK #lobby80K Bob135 :spammer
C2 EXPECT :Ali135!* KICK #lobby80K Bob135 :spammer
