# 91_KICK_ghost_fd_reuse.spec
# Tests that kicking an operator removes their operator status from Channel::operator_fds, preventing ghost operator inheritance if the socket FD is reused.
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice promotes Bob to operator (+o)
C1 SEND MODE #lobby +o Bob
C1 EXPECT :Alice!* MODE #lobby +o Bob
C2 EXPECT :Alice!* MODE #lobby +o Bob

# Alice kicks Bob
C1 SEND KICK #lobby Bob :Demoted
C1 EXPECT :Alice!* KICK #lobby Bob :Demoted
C2 EXPECT :Alice!* KICK #lobby Bob :Demoted

# Bob rejoins #lobby as regular member
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Verify Bob cannot execute operator commands
C2 SEND MODE #lobby +i
C2 EXPECT 482 Bob #lobby :You're not channel operator
