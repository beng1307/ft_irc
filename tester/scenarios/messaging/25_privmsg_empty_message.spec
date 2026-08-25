# PRIVMSG with empty message body (colon but no text).
# Some servers reject this, others accept it. Must handle gracefully.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Empty message (colon present but no text after it) -> 412 ERR_NOTEXTTOSEND
C1 SEND PRIVMSG Bob :
C1 EXPECT 412 Alice :No text to send
C1 SEND PRIVMSG Bob :
C1 EXPECT 412 Alice :No text to send

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
