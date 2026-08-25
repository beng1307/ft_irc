# 53_MODE_ghost_operator_fd_reuse.spec
# Tests security vulnerability: FD recycling ghost operator privilege leak when modifying modes
# Expected: A newly connected client who receives a recycled socket FD is NOT an operator and cannot execute MODE #optest +i.
# Bug: disconnect_client fails to clear operator_fds. A new user with recycled FD automatically becomes channel operator on JOIN and can change modes.
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 creates channel (becomes op @Alice), C2 joins (regular member)
C1 SEND JOIN #optest
C1 EXPECT 353 Alice = #optest :@Alice
C1 EXPECT 366 Alice #optest :End of /NAMES list

C2 SEND JOIN #optest
C1 WAIT_RECV :Bob!* JOIN #optest

# Alice abruptly disconnects and reconnects as Charlie (inheriting the recycled socket FD)
C1 RECONNECT
WAIT 100ms

# Reconnected client registers as Charlie
C1 SEND PASS 1234
C1 SEND NICK Charlie
C1 SEND USER charlie 0 * :Charlie
C1 EXPECT 001 Charlie :*

# Charlie joins #optest
C1 SEND JOIN #optest
C1 EXPECT 353 Charlie = #optest :*Bob*Charlie*

# Charlie attempts to change channel mode to +i; must be rejected with 482 Not channel operator
C1 SEND MODE #optest +i
C1 EXPECT 482 Charlie #optest :You're not channel operator
