# INVITE checks channel membership, operator privilege, target existence, and channel existence.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #inviteerrors
C1 EXPECT :Alice!* JOIN #inviteerrors
C1 SEND MODE #inviteerrors +i
C1 WAIT_RECV :Alice!* MODE #inviteerrors +i
C2 SEND INVITE Nobody #inviteerrors
C2 EXPECT 442 Bob #inviteerrors :You're not on that channel
C2 SEND INVITE Bob #missing
C2 EXPECT 403 Bob #missing :No such channel
C1 SEND INVITE Nobody #inviteerrors
C1 EXPECT 401 Alice Nobody :No such nick/channel
C1 SEND INVITE
C1 EXPECT 461 Alice INVITE :Not enough parameters
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
