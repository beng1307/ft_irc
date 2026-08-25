# 86_KICK_op_on_op.spec
# Tests that an operator can kick another operator, and the kicked operator loses op status upon rejoining.
CLIENTS C1, C2

# Alice registers and creates #lobby86K
C1 SEND PASS 1234
C1 SEND NICK Ali141
C1 SEND USER ali141 0 * :Ali141
C1 EXPECT 001 Ali141 :*
C1 SEND JOIN #lobby86K
C1 EXPECT :Ali141!* JOIN #lobby86K

# Bob registers and joins #lobby86K
C2 SEND PASS 1234
C2 SEND NICK Bob141
C2 SEND USER bob141 0 * :Bob141
C2 EXPECT 001 Bob141 :*
C2 SEND JOIN #lobby86K
C2 EXPECT :Bob141!* JOIN #lobby86K
C1 WAIT_RECV :Bob141!* JOIN #lobby86K

# Alice promotes Bob to operator (+o)
C1 SEND MODE #lobby86K +o Bob141
C1 EXPECT :Ali141!* MODE #lobby86K +o Bob141
C2 EXPECT :Ali141!* MODE #lobby86K +o Bob141

# Alice kicks operator Bob
C1 SEND KICK #lobby86K Bob141 :Demoted and kicked
C1 EXPECT :Ali141!* KICK #lobby86K Bob141 :Demoted and kicked
C2 EXPECT :Ali141!* KICK #lobby86K Bob141 :Demoted and kicked

# Bob rejoins #lobby86K as regular member
C2 SEND JOIN #lobby86K
C2 EXPECT :Bob141!* JOIN #lobby86K
C1 WAIT_RECV :Bob141!* JOIN #lobby86K

# Bob attempts to use operator privileges, expecting rejection
C2 SEND MODE #lobby86K +i
C2 EXPECT 482 Bob141 #lobby86K :You're not channel operator
