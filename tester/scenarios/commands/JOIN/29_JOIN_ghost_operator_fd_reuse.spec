# 29_JOIN_ghost_operator_fd_reuse.spec
# Tests critical security vulnerability: FD recycling ghost operator privilege leak
# Expected: A newly connected client who receives a recycled socket FD does NOT inherit operator privileges in previously joined channels.
# Bug: disconnect_client only removes member_fds, leaving stale FDs in operator_fds. A new user with recycled FD automatically becomes channel operator on JOIN.
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Ali112
C1 SEND USER ali112 0 * :Ali112
C1 EXPECT 001 Ali112 :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob112
C2 SEND USER bob112 0 * :Bob112
C2 EXPECT 001 Bob112 :*

# C1 creates channel (becomes op @Alice), C2 joins (regular member)
C1 SEND JOIN #optest
C1 EXPECT 353 Ali112 = #optest :@Ali112
C1 EXPECT 366 Ali112 #optest :End of /NAMES list

C2 SEND JOIN #optest
C1 WAIT_RECV :Bob112!* JOIN #optest

# Alice abruptly disconnects and reconnects as Charlie (inheriting the recycled socket FD)
C1 RECONNECT
WAIT 100ms

# Reconnected client registers as Charlie
C1 SEND PASS 1234
C1 SEND NICK Cha112
C1 SEND USER cha112 0 * :Cha112
C1 EXPECT 001 Cha112 :*

# Charlie joins #optest
C1 SEND JOIN #optest
# Charlie must NOT have '@' operator prefix in names list
C1 EXPECT 353 Cha112 = #optest :*Bob112*Cha112*

# Charlie attempts to kick Bob; must be rejected with 482 Not channel operator
C1 SEND KICK #optest Bob112 :Unauthorized kick
C1 EXPECT 482 Cha112 #optest :You're not channel operator
