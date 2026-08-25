# INVITE checks channel membership, operator privilege, target existence, and channel existence.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali040
C1 SEND USER ali040 0 * :Ali040
C1 EXPECT 001 Ali040 :*

C2 SEND PASS 1234
C2 SEND NICK Bob040
C2 SEND USER bob040 0 * :Bob040
C2 EXPECT 001 Bob040 :*

C1 SEND JOIN #inviteerrors
C1 EXPECT :Ali040!* JOIN #inviteerrors
C1 SEND MODE #inviteerrors +i
C1 WAIT_RECV :Ali040!* MODE #inviteerrors +i
C2 SEND INVITE Nobody #inviteerrors
C2 EXPECT 442 Bob040 #inviteerrors :You're not on that channel
C2 SEND INVITE Bob040 #missing
C2 EXPECT 403 Bob040 #missing :No such channel
C1 SEND INVITE Nobody #inviteerrors
C1 EXPECT 401 Ali040 Nobody :No such nick/channel
C1 SEND INVITE
C1 EXPECT 461 Ali040 INVITE :Not enough parameters
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
