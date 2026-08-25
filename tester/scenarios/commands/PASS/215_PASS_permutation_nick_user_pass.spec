# 215_PASS_permutation_nick_user_pass.spec
# Registration permutation: NICK -> USER -> PASS
CLIENTS C1

C1 SEND NICK PAlice215
C1 SEND USER ali243 0 * :Ali243 Smith
C1 SEND PASS 1234
C1 EXPECT 001 PAlice215 :*
