# 82_KICK_empty_reason_colon_only.spec
# Tests KICK with empty colon reason (KICK #lobby Bob :).
# Expected: Server sends KICK without trailing parameter or with empty comment.
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

# Alice kicks Bob with empty colon reason
C1 SEND KICK #lobby Bob :
C1 EXPECT :Alice!* KICK #lobby Bob
C2 EXPECT :Alice!* KICK #lobby Bob
