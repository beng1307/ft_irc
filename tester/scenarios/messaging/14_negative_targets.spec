# PRIVMSG reports distinct errors for unknown recipients, channels, and parameters.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 SEND PRIVMSG Nobody :hello
C1 EXPECT 401 Alice Nobody :No such nick/channel
C1 SEND PRIVMSG #missing :hello
C1 EXPECT 403 Alice #missing :No such channel
C1 SEND PRIVMSG
C1 EXPECT 411 Alice :No recipient given (PRIVMSG)
C1 EXPECT_CONNECTED
