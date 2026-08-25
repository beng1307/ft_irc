# 204_PASS_correct_without_colon.spec
# PASS without colon parameter (1234) should be accepted and allow registration
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK PassAliceNorm
C1 SEND USER alicenorm 0 * :Alice Norm
C1 EXPECT 001 PassAliceNorm :*
