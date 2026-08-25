# 172_USER_wrong_password_recovery.spec
# Tests state recovery when client provides wrong PASS with USER, then sends correct PASS
CLIENTS C1

C1 SEND USER ali394 0 * :Ali394 Smith
C1 SEND NICK Ali394
C1 SEND PASS wrongpass
C1 EXPECT 464 Ali394 :Password incorrect

# Client corrects the password
C1 SEND PASS 1234
C1 EXPECT 001 Ali394 :*
C1 EXPECT_CONNECTED
