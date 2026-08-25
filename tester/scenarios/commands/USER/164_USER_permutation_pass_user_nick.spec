# 164_USER_permutation_pass_user_nick.spec
# Registration Permutation 2: PASS -> USER -> NICK
CLIENTS C1

C1 SEND PASS 1234
C1 SEND USER alice 0 * :Alice Smith
C1 SEND NICK Alice
C1 EXPECT 001 Alice :*
C1 EXPECT 002 Alice :*
C1 EXPECT 003 Alice :*
C1 EXPECT 004 Alice *
C1 EXPECT_CONNECTED
