# 103_PRIVMSG_leading_colon_on_target.spec
# Tests PRIVMSG with leading colon on the target parameter (e.g. PRIVMSG :Bob :Hello)
# Strict RFC 1459/2812 behavior: A leading colon ':' designates the start of the final
# trailing parameter. Therefore, ':Bob :Hello Bob' is consumed as a single trailing argument
# ("Bob :Hello Bob"). Since PRIVMSG requires two arguments (<target> <text>), only one
# argument is parsed, resulting in 412 ERR_NOTEXTTOSEND.
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

# C1 sends PRIVMSG with leading colon on recipient (consuming remainder of line as 1 parameter)
C1 SEND PRIVMSG :Bob :Hello Bob
C1 EXPECT 412 Alice :No text to send
C2 NO_RECV :Alice!* PRIVMSG *

