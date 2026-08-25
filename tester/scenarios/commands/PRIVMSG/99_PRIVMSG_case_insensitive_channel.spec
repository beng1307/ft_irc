# 99_PRIVMSG_case_insensitive_channel.spec
# Tests RFC 2812 case-insensitivity when addressing channels via PRIVMSG
# Expected: PRIVMSG #general reaches members of #General
# Bug: Server performs case-sensitive map lookup and returns 403 :No such channel
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali313
C1 SEND USER ali313 0 * :Ali313
C1 EXPECT 001 Ali313 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob313
C2 SEND USER bob313 0 * :Bob313
C2 EXPECT 001 Bob313 :*

# Join channel #General
C1 SEND JOIN #General
C1 EXPECT 366 Ali313 #General :End of /NAMES list
C2 SEND JOIN #General
C1 WAIT_RECV :Bob313!* JOIN #General

# C1 sends message using lowercase #general
C1 SEND PRIVMSG #general :Hello mixed case channel
C2 WAIT_RECV :Ali313!* PRIVMSG #general :Hello mixed case channel
