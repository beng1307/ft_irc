# 91_KICK_ghost_fd_reuse.spec
# Tests that kicking an operator removes their operator status from Channel::operator_fds, preventing ghost operator inheritance if the socket FD is reused.
CLIENTS C1, C2

# Alice registers and creates #lobby91K
C1 SEND PASS 1234
C1 SEND NICK Ali146
C1 SEND USER ali146 0 * :Ali146
C1 EXPECT 001 Ali146 :*
C1 SEND JOIN #lobby91K
C1 EXPECT :Ali146!* JOIN #lobby91K

# Bob registers and joins #lobby91K
C2 SEND PASS 1234
C2 SEND NICK Bob146
C2 SEND USER bob146 0 * :Bob146
C2 EXPECT 001 Bob146 :*
C2 SEND JOIN #lobby91K
C2 EXPECT :Bob146!* JOIN #lobby91K
C1 WAIT_RECV :Bob146!* JOIN #lobby91K

# Alice promotes Bob to operator (+o)
C1 SEND MODE #lobby91K +o Bob146
C1 EXPECT :Ali146!* MODE #lobby91K +o Bob146
C2 EXPECT :Ali146!* MODE #lobby91K +o Bob146

# Alice kicks Bob
C1 SEND KICK #lobby91K Bob146 :Demoted
C1 EXPECT :Ali146!* KICK #lobby91K Bob146 :Demoted
C2 EXPECT :Ali146!* KICK #lobby91K Bob146 :Demoted

# Bob rejoins #lobby91K as regular member
C2 SEND JOIN #lobby91K
C2 EXPECT :Bob146!* JOIN #lobby91K
C1 WAIT_RECV :Bob146!* JOIN #lobby91K

# Verify Bob cannot execute operator commands
C2 SEND MODE #lobby91K +i
C2 EXPECT 482 Bob146 #lobby91K :You're not channel operator
