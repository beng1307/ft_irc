# 124_PART_rapid_double_part_multi.spec
# Tests behavior when a user in a multi-user channel sends PART #chan twice in rapid succession.
# 1st PART succeeds. 2nd PART fails with 442 ERR_NOTONCHANNEL because channel still exists.
CLIENTS C1, C2

# Setup: Alice and Bob join #lobby
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

# Alice sends first PART
C1 SEND PART #lobby :Leaving
C1 EXPECT :Alice!* PART #lobby :Leaving
C2 EXPECT :Alice!* PART #lobby :Leaving

# Alice sends second PART (Bob is still in #lobby so channel exists)
C1 SEND PART #lobby :Leaving again
C1 EXPECT 442 Alice #lobby :You're not on that channel
