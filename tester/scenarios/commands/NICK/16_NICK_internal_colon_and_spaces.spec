# 16_NICK_internal_colon_and_spaces.spec
# Malicious actor attempts to inject spaces inside a nickname using trailing colon notation (:Alice Bob)
# Expected: Nickname with spaces is rejected with 432 Erroneous nickname.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK :Alice Bob
C1 EXPECT 432 * Alice Bob :Erroneous nickname
