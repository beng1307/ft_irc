# PRIVMSG reports distinct errors for unknown recipients, channels, and parameters.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali428
C1 SEND USER ali428 0 * :Ali428
C1 EXPECT 001 Ali428 :*
C1 SEND PRIVMSG Nobody :hello
C1 EXPECT 401 Ali428 Nobody :No such nick/channel
C1 SEND PRIVMSG #missing :hello
C1 EXPECT 403 Ali428 #missing :No such channel
C1 SEND PRIVMSG
C1 EXPECT 411 Ali428 :No recipient given (PRIVMSG)
C1 EXPECT_CONNECTED

