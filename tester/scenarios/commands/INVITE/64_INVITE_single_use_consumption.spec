# 64_INVITE_single_use_consumption.spec
# Tests single-use consumption of invitations upon joining an invite-only (+i) channel.
# Expected: Once a client joins using an invitation, the invitation is consumed. If the client parts, re-joining without a new invitation fails with 473 ERR_INVITEONLYCHAN.
CLIENTS C1, C2

# Alice62 creates invite-only channel
C1 SEND PASS 1234
C1 SEND NICK Ali089
C1 SEND USER ali089 0 * :Ali089
C1 EXPECT 001 Ali089 :*
C1 SEND JOIN #inviteonly62
C1 EXPECT :Ali089!* JOIN #inviteonly62
C1 SEND MODE #inviteonly62 +i
C1 EXPECT :Ali089!* MODE #inviteonly62 +i

# Bob62 registers
C2 SEND PASS 1234
C2 SEND NICK Bob089
C2 SEND USER bob089 0 * :Bob089
C2 EXPECT 001 Bob089 :*

# Alice62 invites Bob62
C1 SEND INVITE Bob089 #inviteonly62
C1 EXPECT 341 Ali089 Bob089 #inviteonly62
C2 WAIT_RECV :Ali089!* INVITE Bob089 :#inviteonly62

# Bob62 joins #inviteonly62 (consuming the invitation)
C2 SEND JOIN #inviteonly62
C2 WAIT_RECV :Bob089!* JOIN #inviteonly62
C1 WAIT_RECV :Bob089!* JOIN #inviteonly62

# Bob62 parts the channel
C2 SEND PART #inviteonly62 :leaving
C1 WAIT_RECV :Bob089!* PART #inviteonly62*
C2 WAIT_RECV :Bob089!* PART #inviteonly62*

# Bob62 tries to rejoin without a new invite
C2 SEND JOIN #inviteonly62
# Must fail because invitation was single-use
C2 EXPECT 473 Bob089 #inviteonly62 :Cannot join channel (+i)
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
