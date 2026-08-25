# 30_JOIN_ghost_invite_fd_reuse.spec
# Tests critical security vulnerability: FD recycling ghost invite bypass (+i)
# Expected: A newly connected client on a recycled socket FD must NOT inherit pending invites sent to previous connections.
# Bug: disconnect_client does not clear invited_fds across all channels. A new client inherits stale invites and bypasses +i restrictions.
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Ali113
C1 SEND USER ali113 0 * :Ali113
C1 EXPECT 001 Ali113 :*

# C1 creates channel and sets invite-only (+i)
C1 SEND JOIN #privchan
C1 SEND MODE #privchan +i
C1 EXPECT :Ali113!* MODE #privchan +i

# C2 connects as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob113
C2 SEND USER bob113 0 * :Bob113
C2 EXPECT 001 Bob113 :*

# Alice invites Bob to #privchan
C1 SEND INVITE Bob113 #privchan
C1 EXPECT 341 Ali113 Bob113 #privchan
C2 WAIT_RECV :Ali113!* INVITE Bob113 :#privchan

# Bob disconnects without joining and reconnects as Charlie (inheriting the recycled socket FD)
C2 RECONNECT
WAIT 100ms

# Charlie authenticates on the recycled socket FD
C2 SEND PASS 1234
C2 SEND NICK Cha113
C2 SEND USER cha113 0 * :Cha113
C2 EXPECT 001 Cha113 :*

# Charlie attempts to join #privchan without an invitation
C2 SEND JOIN #privchan
# Must be rejected with 473 Cannot join channel (+i)
C2 EXPECT 473 Cha113 #privchan :Cannot join channel (+i)
