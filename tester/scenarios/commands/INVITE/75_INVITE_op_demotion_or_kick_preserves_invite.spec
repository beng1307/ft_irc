# 75_INVITE_op_demotion_or_kick_preserves_invite.spec
# Tests that an invitation issued by a legitimate operator remains valid for the target even if the issuing operator is later demoted or leaves.
# Expected: Charlie can join the +i channel using Bob's prior invitation after Bob has been demoted/kicked by Alice.
CLIENTS C1, C2, C3

# Alice creates +i channel and makes Bob an operator
C1 SEND PASS 1234
C1 SEND NICK Ali100
C1 SEND USER ali100 0 * :Ali100
C1 EXPECT 001 Ali100 :*
C1 SEND JOIN #bunker75
C1 EXPECT :Ali100!* JOIN #bunker75
C1 SEND MODE #bunker75 +i
C1 EXPECT :Ali100!* MODE #bunker75 +i

# Bob registers and is invited / joined
C2 SEND PASS 1234
C2 SEND NICK Bob100
C2 SEND USER bob100 0 * :Bob100
C2 EXPECT 001 Bob100 :*
C1 SEND INVITE Bob100 #bunker75
C1 EXPECT 341 Ali100 Bob100 #bunker75
C2 SEND JOIN #bunker75
C2 WAIT_RECV :Bob100!* JOIN #bunker75

# Alice gives Bob channel operator privileges (+o)
C1 SEND MODE #bunker75 +o Bob100
C1 EXPECT :Ali100!* MODE #bunker75 +o Bob100
C2 WAIT_RECV :Ali100!* MODE #bunker75 +o Bob100

# Charlie registers
C3 SEND PASS 1234
C3 SEND NICK Cha100
C3 SEND USER cha100 0 * :Cha100
C3 EXPECT 001 Cha100 :*

# Bob (as operator) invites Charlie
C2 SEND INVITE Cha100 #bunker75
C2 EXPECT 341 Bob100 Cha100 #bunker75
C3 WAIT_RECV :Bob100!* INVITE Cha100 :#bunker75

# Alice demotes and kicks Bob from the channel
C1 SEND MODE #bunker75 -o Bob100
C1 EXPECT :Ali100!* MODE #bunker75 -o Bob100
C1 SEND KICK #bunker75 Bob100 :Goodbye
C1 WAIT_RECV :Ali100!* KICK #bunker75 Bob100 :Goodbye

# Charlie attempts to join #bunker75 -> Must succeed (invitation is recorded in channel state)
C3 SEND JOIN #bunker75
C3 WAIT_RECV :Cha100!* JOIN #bunker75
C1 WAIT_RECV :Cha100!* JOIN #bunker75
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
