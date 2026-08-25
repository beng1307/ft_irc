# 103_PRIVMSG_leading_colon_on_target.spec
# Tests PRIVMSG with leading colon on the target parameter (e.g. PRIVMSG :Bob :Hello)
# Strict RFC 1459/2812 behavior: A leading colon ':' designates the start of the final
# trailing parameter. Therefore, ':Bob :Hello Bob' is consumed as a single trailing argument
# ("Bob :Hello Bob"). Since PRIVMSG requires two arguments (<target> <text>), only one
# argument is parsed, resulting in 412 ERR_NOTEXTTOSEND.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali288
C1 SEND USER ali288 0 * :Ali288
C1 EXPECT 001 Ali288 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob288
C2 SEND USER bob288 0 * :Bob288
C2 EXPECT 001 Bob288 :*

# C1 sends PRIVMSG with leading colon on recipient (consuming remainder of line as 1 parameter)
C1 SEND PRIVMSG :Bob288 :Hello Bob288
C1 EXPECT 412 Ali288 :No text to send
C2 NO_RECV :Ali288!* PRIVMSG *

