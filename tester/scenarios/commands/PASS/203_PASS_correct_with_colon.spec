# 203_PASS_correct_with_colon.spec
# PASS with standard RFC leading colon parameter (:1234) should be accepted and allow registration
CLIENTS C1

C1 SEND PASS :1234
C1 SEND NICK PassAliceCol
C1 SEND USER alicecol 0 * :Alice Col
C1 EXPECT 001 PassAliceCol :*
