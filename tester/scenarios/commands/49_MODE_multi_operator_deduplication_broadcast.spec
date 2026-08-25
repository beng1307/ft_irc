# 49_MODE_multi_operator_deduplication_broadcast.spec
# Tests multi-operator promotion (e.g., MODE #chan +oo Bob Charlie)
# Expected: Server broadcasts valid wire format matching flags with parameters (e.g. MODE #chan +oo Bob Charlie).
# Bug: append_mode_change deduplicates 'o' per sign block, broadcasting malformed "MODE #chan +o Bob Charlie".
CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

C1 SEND JOIN #chan
C1 EXPECT 353 Alice = #chan :@Alice
C1 EXPECT 366 Alice #chan :End of /NAMES list

C2 SEND JOIN #chan
C1 WAIT_RECV :Bob!* JOIN #chan

C3 SEND JOIN #chan
C1 WAIT_RECV :Charlie!* JOIN #chan

# Promote both Bob and Charlie in single command
C1 SEND MODE #chan +oo Bob Charlie
C1 EXPECT :Alice!* MODE #chan +oo Bob Charlie
C2 EXPECT :Alice!* MODE #chan +oo Bob Charlie
C3 EXPECT :Alice!* MODE #chan +oo Bob Charlie
