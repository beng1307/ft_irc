# 171_USER_pre_registration_overwrite.spec
# Tests multiple USER commands sent BEFORE registration is completed
# Expected: The last USER command before registration overwrites previous ones.
CLIENTS C1, C2

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #testchan
C2 EXPECT 353 Bob = #testchan :@Bob

C1 SEND USER firstuser 0 * :First Name
C1 SEND USER finaluser 0 * :Final Name
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #testchan
C2 EXPECT :Alice!finaluser@localhost JOIN #testchan
