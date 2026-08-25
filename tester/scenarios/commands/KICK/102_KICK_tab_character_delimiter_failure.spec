# 102_KICK_tab_character_delimiter_failure.spec
# Tests that tab characters (\t) used as command parameter delimiters are strictly rejected per RFC 2812 §2.3.1.
# Expected: Server fails channel lookup with 403 ERR_NOSUCHCHANNEL because spaces (0x20) are the only valid IRC parameter delimiters.
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

# Alice sends KICK with tab delimiter between channel and target
C1 SEND KICK #lobby	Bob :tab test
C1 EXPECT 403 Alice #lobby	Bob :No such channel
