# 259_PASS_colon_space_preservation.spec
# PASS : 1234 (colon followed by space) includes the leading space in password (' 1234'), which fails comparison
CLIENTS C1

C1 SEND PASS : 1234
C1 EXPECT 464 * :Password incorrect
