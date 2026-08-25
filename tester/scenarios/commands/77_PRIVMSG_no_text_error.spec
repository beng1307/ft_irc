# 47_PRIVMSG_no_text_error.spec
# Tests PRIVMSG with recipient but no text payload (missing or empty colon)
# Expected: 412 ERR_NOTEXTTOSEND (:No text to send)
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 sends PRIVMSG with no payload
C1 SEND PRIVMSG Bob
C1 EXPECT 412 Alice :No text to send

# C1 sends PRIVMSG with empty colon payload
C1 SEND PRIVMSG Bob :
C1 EXPECT 412 Alice :No text to send
