# 79_INVITE_kick_purges_all_pending_and_active_invite.spec
# Tests that when an invited user is kicked from a channel, all invitations are wiped clean.
# Expected: Even if +i mode is temporarily removed and re-enabled, the kicked user cannot rejoin without a fresh invitation.
CLIENTS C1, C2

# Alice creates +i channel and invites Bob
C1 SEND PASS 1234
C1 SEND NICK Alice79
C1 SEND USER alice79 0 * :Alice
C1 EXPECT 001 Alice79 :*
C1 SEND JOIN #secure79
C1 EXPECT :Alice79!* JOIN #secure79
C1 SEND MODE #secure79 +i
C1 EXPECT :Alice79!* MODE #secure79 +i

# Bob registers and joins via invite
C2 SEND PASS 1234
C2 SEND NICK Bob79
C2 SEND USER bob79 0 * :Bob
C2 EXPECT 001 Bob79 :*
C1 SEND INVITE Bob79 #secure79
C1 EXPECT 341 Alice79 Bob79 #secure79
C2 SEND JOIN #secure79
C2 WAIT_RECV :Bob79!* JOIN #secure79

# Alice removes +i, kicks Bob, then re-adds +i
C1 SEND MODE #secure79 -i
C1 EXPECT :Alice79!* MODE #secure79 -i
C1 SEND KICK #secure79 Bob79 :Banned
C1 WAIT_RECV :Alice79!* KICK #secure79 Bob79 :Banned
C1 SEND MODE #secure79 +i
C1 EXPECT :Alice79!* MODE #secure79 +i

# Bob tries to rejoin #secure79 -> Blocked with 473 Cannot join channel (+i)
C2 SEND JOIN #secure79
C2 EXPECT 473 Bob79 #secure79 :Cannot join channel (+i)
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
