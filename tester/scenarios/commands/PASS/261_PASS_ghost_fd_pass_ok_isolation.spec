# 261_PASS_ghost_fd_pass_ok_isolation.spec
# Memory / FD Isolation: FD reuse must not leak pass_ok=true from a previous client
CLIENTS C1, C2

# C1 authenticates then terminates connection
C1 SEND PASS 1234
C1 SEND QUIT :Exiting
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# C2 connects without sending PASS; must not inherit authentication
C2 SEND NICK PassGhost
C2 SEND USER passghost 0 * :Ghost Usr260
C2 SEND JOIN #test
C2 EXPECT 451 * :You have not registered
