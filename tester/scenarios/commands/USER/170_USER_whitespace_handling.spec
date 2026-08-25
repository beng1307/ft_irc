# 170_USER_whitespace_handling.spec
# Tests USER command with extra whitespace between tokens
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali392
C1 SEND USER    ali392    0    *    :Ali392 Smith
C1 EXPECT 001 Ali392 :*
C1 EXPECT_CONNECTED
