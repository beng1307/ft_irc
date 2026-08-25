# A duplicate nickname is rejected, then the client can register under a new nick.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali451
C1 SEND USER ali451 0 * :Ali451
C1 EXPECT 001 Ali451 :*

C2 SEND PASS 1234
C2 SEND NICK Ali451
C2 EXPECT 433 * Ali451 :Nickname is already in use
C2 SEND NICK Bob451
C2 SEND USER bob451 0 * :Bob451
C2 EXPECT 001 Bob451 :*
C2 EXPECT_CONNECTED

