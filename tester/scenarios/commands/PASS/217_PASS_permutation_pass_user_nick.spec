# 217_PASS_permutation_pass_user_nick.spec
# Registration permutation: PASS -> USER -> NICK
CLIENTS C1

C1 SEND PASS 1234
C1 SEND USER alice217 0 * :Alice Smith
C1 SEND NICK PAlice217
C1 EXPECT 001 PAlice217 :*
