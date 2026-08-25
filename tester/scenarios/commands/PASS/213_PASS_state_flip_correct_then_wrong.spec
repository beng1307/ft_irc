# 213_PASS_state_flip_correct_then_wrong.spec
# Sending correct PASS then incorrect PASS flips pass_ok to false, blocking registration
CLIENTS C1

C1 SEND PASS 1234
C1 SEND PASS wrongpassword
C1 EXPECT 464 * :Password incorrect

C1 SEND NICK Ali241
C1 SEND USER ali241 0 * :Ali241 Smith

# Registration should NOT happen, commands must fail with 451
C1 SEND JOIN #test
C1 EXPECT 451 * :You have not registered
