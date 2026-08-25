# 171_USER_pre_registration_overwrite.spec
# Tests multiple USER commands sent BEFORE registration is completed
# Expected: The last USER command before registration overwrites previous ones.
CLIENTS C1, C2

C2 SEND PASS 1234
C2 SEND NICK Bob393
C2 SEND USER bob393 0 * :Bob393
C2 EXPECT 001 Bob393 :*
C2 SEND JOIN #testchan
C2 EXPECT 353 Bob393 = #testchan :@Bob393

C1 SEND USER u1st393 0 * :First Name
C1 SEND USER ufin393 0 * :Final Name
C1 SEND PASS 1234
C1 SEND NICK Ali393
C1 EXPECT 001 Ali393 :*

C1 SEND JOIN #testchan
C2 EXPECT :Ali393!ufin393@localhost JOIN #testchan
