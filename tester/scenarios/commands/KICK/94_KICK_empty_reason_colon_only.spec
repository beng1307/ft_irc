# 94_KICK_empty_reason_colon_only.spec
# Tests KICK with empty colon reason (KICK #lobby Bob :).
# Expected: Server sends KICK without trailing parameter or with empty comment.
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali149
C1 SEND USER ali149 0 * :Ali149
C1 EXPECT 001 Ali149 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali149!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob149
C2 SEND USER bob149 0 * :Bob149
C2 EXPECT 001 Bob149 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob149!* JOIN #lobby
C1 WAIT_RECV :Bob149!* JOIN #lobby

# Alice kicks Bob with empty colon reason
C1 SEND KICK #lobby Bob149 :
C1 EXPECT :Ali149!* KICK #lobby Bob149
C2 EXPECT :Ali149!* KICK #lobby Bob149
