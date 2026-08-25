# 150_PART_broadcast_to_self_and_members.spec
# Tests that PART broadcast is delivered to BOTH the parting client and all other channel members.
CLIENTS C1, C2, C3

# Alice, Bob, Charlie join #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*
C3 SEND JOIN #lobby
C3 EXPECT :Charlie!* JOIN #lobby
C1 WAIT_RECV :Charlie!* JOIN #lobby
C2 WAIT_RECV :Charlie!* JOIN #lobby

# Bob parts #lobby
C2 SEND PART #lobby :See ya
C2 EXPECT :Bob!* PART #lobby :See ya
C1 EXPECT :Bob!* PART #lobby :See ya
C3 EXPECT :Bob!* PART #lobby :See ya
