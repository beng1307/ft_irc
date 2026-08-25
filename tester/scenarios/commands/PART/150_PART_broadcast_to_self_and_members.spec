# 150_PART_broadcast_to_self_and_members.spec
# Tests that PART broadcast is delivered to BOTH the parting client and all other channel members.
CLIENTS C1, C2, C3

# Alice, Bob, Charlie join #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali219
C1 SEND USER ali219 0 * :Ali219
C1 EXPECT 001 Ali219 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali219!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob219
C2 SEND USER bob219 0 * :Bob219
C2 EXPECT 001 Bob219 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob219!* JOIN #lobby
C1 WAIT_RECV :Bob219!* JOIN #lobby

C3 SEND PASS 1234
C3 SEND NICK Cha219
C3 SEND USER cha219 0 * :Cha219
C3 EXPECT 001 Cha219 :*
C3 SEND JOIN #lobby
C3 EXPECT :Cha219!* JOIN #lobby
C1 WAIT_RECV :Cha219!* JOIN #lobby
C2 WAIT_RECV :Cha219!* JOIN #lobby

# Bob parts #lobby
C2 SEND PART #lobby :See ya
C2 EXPECT :Bob219!* PART #lobby :See ya
C1 EXPECT :Bob219!* PART #lobby :See ya
C3 EXPECT :Bob219!* PART #lobby :See ya
