# 210_PASS_password_with_spaces_in_colon.spec
# Leading colon includes spaces in password argument; since server password is '1234', ':1234 extra' fails with 464
CLIENTS C1

C1 SEND PASS :1234 extra
C1 EXPECT 464 * :Password incorrect
