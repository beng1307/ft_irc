# 288_USER_multi_word_realname_without_colon.spec
# Tests USER command with multi-word realname provided without leading colon (5+ tokens)
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * John Doe Smith
C1 EXPECT 001 Alice :*
C1 EXPECT 002 Alice :*
C1 EXPECT 003 Alice :*
C1 EXPECT 004 Alice *
C1 EXPECT_CONNECTED
