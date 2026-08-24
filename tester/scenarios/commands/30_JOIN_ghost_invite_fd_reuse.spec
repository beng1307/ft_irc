# 30_JOIN_ghost_invite_fd_reuse.spec
# Tests critical security vulnerability: FD recycling ghost invite bypass (+i)
# Expected: A newly connected client on a recycled socket FD must NOT inherit pending invites sent to previous connections.
# Bug: disconnect_client does not clear invited_fds across all channels. A new client inherits stale invites and bypasses +i restrictions.
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C1 creates channel and sets invite-only (+i)
C1 SEND JOIN #privchan
C1 SEND MODE #privchan +i
C1 EXPECT :Alice!* MODE #privchan +i

# C2 connects as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice invites Bob to #privchan
C1 SEND INVITE Bob #privchan
C1 EXPECT 341 Alice Bob #privchan
C2 WAIT_RECV :Alice!* INVITE Bob :#privchan

# Bob disconnects without joining and reconnects as Charlie (inheriting the recycled socket FD)
C2 RECONNECT
WAIT 100ms

# Charlie authenticates on the recycled socket FD
C2 SEND PASS 1234
C2 SEND NICK Charlie
C2 SEND USER charlie 0 * :Charlie
C2 EXPECT 001 Charlie :*

# Charlie attempts to join #privchan without an invitation
C2 SEND JOIN #privchan
# Must be rejected with 473 Cannot join channel (+i)
C2 EXPECT 473 Charlie #privchan :Cannot join channel (+i)
