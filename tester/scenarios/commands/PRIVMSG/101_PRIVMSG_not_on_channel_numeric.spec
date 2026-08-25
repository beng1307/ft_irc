# 101_PRIVMSG_not_on_channel_numeric.spec
# Tests RFC 2812 standard error numeric when non-member sends message to channel
# Expected: Server replies with 404 ERR_CANNOTSENDTOCHAN (#chan :Cannot send to channel)
# Bug: Server replies with 442 ERR_NOTONCHANNEL instead of standard 404
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali286
C1 SEND USER ali286 0 * :Ali286
C1 EXPECT 001 Ali286 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob286
C2 SEND USER bob286 0 * :Bob286
C2 EXPECT 001 Bob286 :*

# C2 creates channel #private
C2 SEND JOIN #private
C2 EXPECT 366 Bob286 #private :End of /NAMES list

# C1 (not in #private) sends message to #private
C1 SEND PRIVMSG #private :Can I talk?
C1 EXPECT 404 Ali286 #private :Cannot send to channel
