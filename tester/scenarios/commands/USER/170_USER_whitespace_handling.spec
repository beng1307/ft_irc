# 170_USER_whitespace_handling.spec
# Tests USER command with extra whitespace between tokens
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER    alice    0    *    :Alice Smith
C1 EXPECT 001 Alice :*
C1 EXPECT_CONNECTED
