# 288_USER_multi_word_realname_without_colon.spec
# Tests USER command with multi-word realname provided without leading colon (5+ tokens)
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali410
C1 SEND USER ali410 0 * John Doe Smith
C1 EXPECT 001 Ali410 :*
C1 EXPECT 002 Ali410 :*
C1 EXPECT 003 Ali410 :*
C1 EXPECT 004 Ali410 *
C1 EXPECT_CONNECTED
