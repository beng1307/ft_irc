# 59_INVITE_ghost_invite_fd_reuse.spec
# Tests critical security vulnerability: FD recycling ghost invite bypass (+i)
# Expected: A newly connected client on a recycled socket FD must NOT inherit pending invites sent to previous connections.
# Bug: disconnect_client does not clear invited_fds across channels. A new client inherits stale invites and bypasses +i restrictions.
CLIENTS C1, C2

# Alice57 registers and creates invite-only (+i) channel
C1 SEND PASS 1234
C1 SEND NICK Ali084
C1 SEND USER ali084 0 * :Ali084
C1 EXPECT 001 Ali084 :*
C1 SEND JOIN #privchan57
C1 EXPECT :Ali084!* JOIN #privchan57
C1 SEND MODE #privchan57 +i
C1 EXPECT :Ali084!* MODE #privchan57 +i

# Bob57 connects and registers
C2 SEND PASS 1234
C2 SEND NICK Bob084
C2 SEND USER bob084 0 * :Bob084
C2 EXPECT 001 Bob084 :*

# Alice57 invites Bob57 to #privchan57
C1 SEND INVITE Bob084 #privchan57
C1 EXPECT 341 Ali084 Bob084 #privchan57
C2 WAIT_RECV :Ali084!* INVITE Bob084 :#privchan57

# Bob57 disconnects without joining and reconnects as Charlie57 (inheriting recycled socket FD)
C2 RECONNECT
WAIT 100ms

# Charlie57 authenticates on recycled socket FD
C2 SEND PASS 1234
C2 SEND NICK Cha084
C2 SEND USER cha084 0 * :Cha084
C2 EXPECT 001 Cha084 :*

# Charlie57 attempts to join #privchan57 without an invitation
C2 SEND JOIN #privchan57
# Must be rejected with 473 Cannot join channel (+i)
C2 EXPECT 473 Cha084 #privchan57 :Cannot join channel (+i)
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
