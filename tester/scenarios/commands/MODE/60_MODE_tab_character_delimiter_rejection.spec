# 60_MODE_tab_character_delimiter_rejection.spec
# Adversarial Input: Using ASCII TAB (\t) characters instead of standard spaces.
# Expected: Server conforms to RFC BNF syntax requiring spaces as command delimiters; tabs are rejected or treated as invalid tokens.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali177
C1 SEND USER ali177 0 * :Ali177
C1 EXPECT 001 Ali177 :*

C1 SEND JOIN #tabtest60
C1 EXPECT 353 Ali177 = #tabtest60 :@Ali177
C1 EXPECT 366 Ali177 #tabtest60 :End of /NAMES list

# Send MODE with tab character
C1 SEND_RAW MODE\t#tabtest60\t+i\r\n
# Expected: 421 Unknown command error response
C1 EXPECT 421 Ali177 Unknown command.
