# A direct message reaches only its target, while a channel message reaches other members.
CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie

C1 SEND PRIVMSG Bob :private
C2 WAIT_RECV :Alice!* PRIVMSG Bob :private
C3 EXPECT_NONE 150ms

C1 SEND JOIN #isolation
C2 SEND JOIN #isolation
C3 SEND JOIN #isolation
C1 WAIT_RECV :Charlie!* JOIN #isolation
C1 SEND PRIVMSG #isolation :group
C2 WAIT_RECV :Alice!* PRIVMSG #isolation :group
C3 WAIT_RECV :Alice!* PRIVMSG #isolation :group

