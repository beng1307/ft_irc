# 71_INVITE_empty_channel_recreated_clean.spec
# Tests that when an invite-only channel is completely emptied (destroyed), pending invitations are wiped.
# Expected: If the channel is recreated by a new user with +i, the previous invitee cannot join without a new invite.
CLIENTS C1, C2, C3

# Alice creates +i channel and invites Bob
C1 SEND PASS 1234
C1 SEND NICK Ali096
C1 SEND USER ali096 0 * :Ali096
C1 EXPECT 001 Ali096 :*
C1 SEND JOIN #recreated69
C1 EXPECT :Ali096!* JOIN #recreated69
C1 SEND MODE #recreated69 +i
C1 EXPECT :Ali096!* MODE #recreated69 +i

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob096
C2 SEND USER bob096 0 * :Bob096
C2 EXPECT 001 Bob096 :*

# Alice invites Bob
C1 SEND INVITE Bob096 #recreated69
C1 EXPECT 341 Ali096 Bob096 #recreated69
C2 WAIT_RECV :Ali096!ali096@localhost INVITE Bob096 :#recreated69

# Alice leaves the channel, destroying the channel instance
C1 SEND PART #recreated69 :bye
C1 WAIT_RECV :Ali096!* PART #recreated69*

# Charlie recreates #recreated69 and sets +i
C3 SEND PASS 1234
C3 SEND NICK Cha096
C3 SEND USER cha096 0 * :Cha096
C3 EXPECT 001 Cha096 :*
C3 SEND JOIN #recreated69
C3 EXPECT :Cha096!* JOIN #recreated69
C3 SEND MODE #recreated69 +i
C3 EXPECT :Cha096!* MODE #recreated69 +i

# Bob tries to join using the old invitation from Alice
C2 SEND JOIN #recreated69
# Must be rejected because old channel state was wiped on destruction
C2 EXPECT 473 Bob096 #recreated69 :Cannot join channel (+i)
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
