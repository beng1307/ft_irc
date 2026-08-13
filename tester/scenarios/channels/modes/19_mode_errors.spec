# Invalid MODE operations are rejected without disconnecting the clients.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C1 SEND JOIN #modeerrors
C2 SEND MODE #modeerrors +i
C2 EXPECT 442 Bob #modeerrors :You're not on that channel
C2 SEND MODE #missing +i
C2 EXPECT 403 Bob #missing :No such channel
C1 SEND MODE #modeerrors +k
C1 EXPECT 461 Alice MODE :Not enough parameters
C1 SEND MODE #modeerrors +z
C1 EXPECT 472 Alice z :is unknown mode char to me
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
