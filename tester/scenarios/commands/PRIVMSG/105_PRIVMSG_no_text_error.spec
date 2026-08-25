# 105_PRIVMSG_no_text_error.spec
# Tests PRIVMSG with recipient but no text payload (missing or empty colon)
# Expected: 412 ERR_NOTEXTTOSEND (:No text to send)
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali290
C1 SEND USER ali290 0 * :Ali290
C1 EXPECT 001 Ali290 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob290
C2 SEND USER bob290 0 * :Bob290
C2 EXPECT 001 Bob290 :*

# C1 sends PRIVMSG with no payload
C1 SEND PRIVMSG Bob290
C1 EXPECT 412 Ali290 :No text to send

# C1 sends PRIVMSG with empty colon payload
C1 SEND PRIVMSG Bob290 :
C1 EXPECT 412 Ali290 :No text to send
