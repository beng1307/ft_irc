# 206_PASS_case_sensitivity_password.spec
# Password comparison is strictly case-sensitive. PASS 1234 != PASS 1234abcd
CLIENTS C1

C1 SEND PASS 1234ABCD
C1 EXPECT 464 * :Password incorrect
