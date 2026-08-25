# 68_KICK_single_word_reason_without_colon.spec
# Tests RFC 2812 §3.2.8 single-word comment without leading colon.
# Expected: Server extracts 'spammer' as the kick comment and broadcasts ':Alice!* KICK #lobby Bob :spammer'.
# Bug: Server strictly checks for ' :' (line.contains(" :")), failing when no colon is supplied and silently replacing the reason with the kicker's own nickname.
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice kicks Bob with single-word reason 'spammer' (no colon)
C1 SEND KICK #lobby Bob spammer
C1 EXPECT :Alice!* KICK #lobby Bob :spammer
C2 EXPECT :Alice!* KICK #lobby Bob :spammer
