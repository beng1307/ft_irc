# 287_USER_trailing_parameters_with_internal_colons.spec
# Tests RFC trailing parameter parsing when realname contains multiple internal colons
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Real:Name:With::Multiple:::Colons
C1 EXPECT 001 Alice :*
C1 EXPECT 002 Alice :*
C1 EXPECT 003 Alice :*
C1 EXPECT 004 Alice *
C1 EXPECT_CONNECTED
