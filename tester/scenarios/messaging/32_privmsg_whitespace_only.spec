# PRIVMSG with only whitespace as message content.
# "PRIVMSG Bob : " (space after colon) - should be valid message.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali438
C1 SEND USER ali438 0 * :Ali438
C1 EXPECT 001 Ali438 :*

C2 SEND PASS 1234
C2 SEND NICK Bob438
C2 SEND USER bob438 0 * :Bob438
C2 EXPECT 001 Bob438 :*

# Message with only spaces after colon (use SEND_RAW so test runner trim does not strip trailing spaces)
C1 SEND_RAW PRIVMSG Bob438 :   \r\n
C2 WAIT_RECV :Ali438!* PRIVMSG Bob438 :   

# Message with only a single space
C1 SEND_RAW PRIVMSG Bob438 : \r\n
C2 WAIT_RECV :Ali438!* PRIVMSG Bob438 : 

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
