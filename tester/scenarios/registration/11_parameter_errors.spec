# Missing command parameters return errors and leave the connection usable.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK
C1 EXPECT 431 * :No nickname given
C1 SEND USER
C1 EXPECT 461 * USER :Not enough parameters
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT_CONNECTED
