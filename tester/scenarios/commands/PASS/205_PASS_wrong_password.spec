# 205_PASS_wrong_password.spec
# PASS with incorrect password returns 464 ERR_PASSWDMISMATCH
CLIENTS C1

C1 SEND PASS wrongpassword
C1 EXPECT 464 * :Password incorrect
