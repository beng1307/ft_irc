# PRIVMSG with empty message body (colon but no text).
# Some servers reject this, others accept it. Must handle gracefully.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali430
C1 SEND USER ali430 0 * :Ali430
C1 EXPECT 001 Ali430 :*

C2 SEND PASS 1234
C2 SEND NICK Bob430
C2 SEND USER bob430 0 * :Bob430
C2 EXPECT 001 Bob430 :*

# Empty message (colon present but no text after it) -> 412 ERR_NOTEXTTOSEND
C1 SEND PRIVMSG Bob430 :
C1 EXPECT 412 Ali430 :No text to send
C1 SEND PRIVMSG Bob430 :
C1 EXPECT 412 Ali430 :No text to send

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
