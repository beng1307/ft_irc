# 60_MODE_tab_character_delimiter_rejection.spec
# Adversarial Input: Using ASCII TAB (\t) characters instead of standard spaces.
# Expected: Server conforms to RFC BNF syntax requiring spaces as command delimiters; tabs are rejected or treated as invalid tokens.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice60
C1 SEND USER alice60 0 * :Alice60
C1 EXPECT 001 Alice60 :*

C1 SEND JOIN #tabtest60
C1 EXPECT 353 Alice60 = #tabtest60 :@Alice60
C1 EXPECT 366 Alice60 #tabtest60 :End of /NAMES list

# Send MODE with tab character
C1 SEND_RAW MODE\t#tabtest60\t+i\r\n
# Expected: 421 Unknown command error response
C1 EXPECT 421 Alice60 Unknown command.
