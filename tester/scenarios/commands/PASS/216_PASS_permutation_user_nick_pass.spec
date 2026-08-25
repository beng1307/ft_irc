# 216_PASS_permutation_user_nick_pass.spec
# Registration permutation: USER -> NICK -> PASS
CLIENTS C1

C1 SEND USER alice216 0 * :Alice Smith
C1 SEND NICK PassAlice216
C1 SEND PASS 1234
C1 EXPECT 001 PassAlice216 :*
