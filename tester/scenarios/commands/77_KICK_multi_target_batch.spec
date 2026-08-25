# 77_KICK_multi_target_batch.spec
# Tests RFC 2812 §3.2.8 comma-separated multi-user batch kick (KICK #lobby Bob,Charlie :batch).
# Expected: Server parses the comma-separated user list, kicking both Bob and Charlie.
# Bug: Server treats 'Bob,Charlie' as a single literal nickname, searching for client 'Bob,Charlie' and failing with 401 ERR_NOSUCHNICK.
CLIENTS C1, C2, C3

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

# Charlie registers and joins #lobby
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*
C3 SEND JOIN #lobby
C3 EXPECT :Charlie!* JOIN #lobby
C1 WAIT_RECV :Charlie!* JOIN #lobby
C2 WAIT_RECV :Charlie!* JOIN #lobby

# Alice batch-kicks both Bob and Charlie
C1 SEND KICK #lobby Bob,Charlie :batch cleanup
C1 EXPECT :Alice!* KICK #lobby Bob :batch cleanup
C1 EXPECT :Alice!* KICK #lobby Charlie :batch cleanup
C2 EXPECT :Alice!* KICK #lobby Bob :batch cleanup
C3 EXPECT :Alice!* KICK #lobby Charlie :batch cleanup
