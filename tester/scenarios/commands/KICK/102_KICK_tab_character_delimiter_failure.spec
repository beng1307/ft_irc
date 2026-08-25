# 102_KICK_tab_character_delimiter_failure.spec
# Tests that tab characters (\t) used as command parameter delimiters are strictly rejected per RFC 2812 §2.3.1.
# Expected: Server fails channel lookup with 403 ERR_NOSUCHCHANNEL because spaces (0x20) are the only valid IRC parameter delimiters.
CLIENTS C1, C2

# Alice registers and creates #lobby102K
C1 SEND PASS 1234
C1 SEND NICK Ali123
C1 SEND USER ali123 0 * :Ali123
C1 EXPECT 001 Ali123 :*
C1 SEND JOIN #lobby102K
C1 EXPECT :Ali123!* JOIN #lobby102K

# Bob registers and joins #lobby102K
C2 SEND PASS 1234
C2 SEND NICK Bob123
C2 SEND USER bob123 0 * :Bob123
C2 EXPECT 001 Bob123 :*
C2 SEND JOIN #lobby102K
C2 EXPECT :Bob123!* JOIN #lobby102K
C1 WAIT_RECV :Bob123!* JOIN #lobby102K

# Alice sends KICK with tab delimiter between channel and target
C1 SEND KICK #lobby102K	Bob123 :tab test
C1 EXPECT 403 Ali123 #lobby102K	Bob123 :No such channel
