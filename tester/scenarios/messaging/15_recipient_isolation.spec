# A direct message reaches only its target, while a channel message reaches other members.
CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali429
C1 SEND USER ali429 0 * :Ali429
C1 EXPECT 001 Ali429 :*

C2 SEND PASS 1234
C2 SEND NICK Bob429
C2 SEND USER bob429 0 * :Bob429
C2 EXPECT 001 Bob429 :*

C3 SEND PASS 1234
C3 SEND NICK Cha429
C3 SEND USER cha429 0 * :Cha429
C3 EXPECT 004 Cha429 *

C1 SEND PRIVMSG Bob429 :private
C2 WAIT_RECV :Ali429!* PRIVMSG Bob429 :private
C3 EXPECT_NONE 150ms

C1 SEND JOIN #isolation
C1 EXPECT :Ali429!* JOIN #isolation
C2 SEND JOIN #isolation
C2 WAIT_RECV :Bob429!* JOIN #isolation
C1 WAIT_RECV :Bob429!* JOIN #isolation
C3 SEND JOIN #isolation
C3 WAIT_RECV :Cha429!* JOIN #isolation
C1 WAIT_RECV :Cha429!* JOIN #isolation

C1 SEND PRIVMSG #isolation :group
C2 WAIT_RECV :Ali429!* PRIVMSG #isolation :group
C3 WAIT_RECV :Ali429!* PRIVMSG #isolation :group
