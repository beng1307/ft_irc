# 172_USER_wrong_password_recovery.spec
# Tests state recovery when client provides wrong PASS with USER, then sends correct PASS
CLIENTS C1

C1 SEND USER alice 0 * :Alice Smith
C1 SEND NICK Alice
C1 SEND PASS wrongpass
C1 EXPECT 464 Alice :Password incorrect

# Client corrects the password
C1 SEND PASS 1234
C1 EXPECT 001 Alice :*
C1 EXPECT_CONNECTED
