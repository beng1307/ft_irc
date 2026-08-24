# PRIVMSG with only whitespace as message content.
# "PRIVMSG Bob : " (space after colon) - should be valid message.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Message with only spaces after colon
C1 SEND PRIVMSG Bob :   
C2 WAIT_RECV :Alice!* PRIVMSG Bob :   

# Message with only a single space
C1 SEND PRIVMSG Bob : 
C2 WAIT_RECV :Alice!* PRIVMSG Bob : 

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
