# 46_MODE_multi_operator_deduplication_broadcast.spec
# Tests multi-operator promotion (e.g., MODE #chan +oo Bob Charlie)
# Expected: Server broadcasts valid wire format matching flags with parameters (e.g. MODE #chan +oo Bob Charlie).
# Bug: append_mode_change deduplicates 'o' per sign block, broadcasting malformed "MODE #chan +o Bob Charlie".
CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali163
C1 SEND USER ali163 0 * :Ali163
C1 EXPECT 001 Ali163 :*

C2 SEND PASS 1234
C2 SEND NICK Bob163
C2 SEND USER bob163 0 * :Bob163
C2 EXPECT 001 Bob163 :*

C3 SEND PASS 1234
C3 SEND NICK Cha163
C3 SEND USER cha163 0 * :Cha163
C3 EXPECT 001 Cha163 :*

C1 SEND JOIN #chan
C1 EXPECT 353 Ali163 = #chan :@Ali163
C1 EXPECT 366 Ali163 #chan :End of /NAMES list

C2 SEND JOIN #chan
C1 WAIT_RECV :Bob163!* JOIN #chan

C3 SEND JOIN #chan
C1 WAIT_RECV :Cha163!* JOIN #chan

# Promote both Bob and Charlie in single command
C1 SEND MODE #chan +oo Bob163 Cha163
C1 EXPECT :Ali163!* MODE #chan +oo Bob163 Cha163
C2 EXPECT :Ali163!* MODE #chan +oo Bob163 Cha163
C3 EXPECT :Ali163!* MODE #chan +oo Bob163 Cha163
