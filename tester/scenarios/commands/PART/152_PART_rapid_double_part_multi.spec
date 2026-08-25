# 152_PART_rapid_double_part_multi.spec
# Tests behavior when a user in a multi-user channel sends PART #chan twice in rapid succession.
# 1st PART succeeds. 2nd PART fails with 442 ERR_NOTONCHANNEL because channel still exists.
CLIENTS C1, C2

# Setup: Alice and Bob join #lobby152P
C1 SEND PASS 1234
C1 SEND NICK Ali221
C1 SEND USER ali221 0 * :Ali221
C1 EXPECT 001 Ali221 :*
C1 SEND JOIN #lobby152P
C1 EXPECT :Ali221!* JOIN #lobby152P

C2 SEND PASS 1234
C2 SEND NICK Bob221
C2 SEND USER bob221 0 * :Bob221
C2 EXPECT 001 Bob221 :*
C2 SEND JOIN #lobby152P
C2 EXPECT :Bob221!* JOIN #lobby152P
C1 WAIT_RECV :Bob221!* JOIN #lobby152P

# Alice sends first PART
C1 SEND PART #lobby152P :Leaving
C1 EXPECT :Ali221!* PART #lobby152P :Leaving
C2 EXPECT :Ali221!* PART #lobby152P :Leaving

# Alice sends second PART (Bob is still in #lobby152P so channel exists)
C1 SEND PART #lobby152P :Leaving again
C1 EXPECT 442 Ali221 #lobby152P :You're not on that channel
