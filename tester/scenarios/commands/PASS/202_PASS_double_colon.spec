# 202_PASS_double_colon.spec
# PASS ::1234 strips the first colon and treats ':1234' as the password, which mismatches '1234'
CLIENTS C1

C1 SEND PASS ::1234
C1 EXPECT 464 * :Password incorrect
