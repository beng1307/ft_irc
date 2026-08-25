# Invalid MODE operations are rejected without disconnecting the clients.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali052
C1 SEND USER ali052 0 * :Ali052
C1 EXPECT 001 Ali052 :*

C2 SEND PASS 1234
C2 SEND NICK Bob052
C2 SEND USER bob052 0 * :Bob052
C2 EXPECT 001 Bob052 :*

C1 SEND JOIN #modeerrors
C1 EXPECT :Ali052!* JOIN #modeerrors
C2 SEND MODE #modeerrors +i
C2 EXPECT 442 Bob052 #modeerrors :You're not on that channel
C2 SEND MODE #missing +i
C2 EXPECT 403 Bob052 #missing :No such channel
C1 SEND MODE #modeerrors +k
C1 EXPECT 461 Ali052 MODE :Not enough parameters
C1 SEND MODE #modeerrors +z
C1 EXPECT 472 Ali052 z :is unknown mode char to me
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
