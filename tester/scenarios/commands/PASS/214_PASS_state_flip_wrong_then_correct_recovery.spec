# 214_PASS_state_flip_wrong_then_correct_recovery.spec
# Sending wrong password then correct password allows client to recover and successfully register
CLIENTS C1

C1 SEND PASS wrongpass
C1 EXPECT 464 * :Password incorrect

C1 SEND PASS 1234
C1 SEND NICK PAlice214
C1 SEND USER ali242 0 * :Ali242 Smith
C1 EXPECT 001 PAlice214 :*
