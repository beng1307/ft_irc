# 99_PRIVMSG_case_insensitive_channel.spec
# Tests RFC 2812 case-insensitivity when addressing channels via PRIVMSG
# Expected: PRIVMSG #general reaches members of #General
# Bug: Server performs case-sensitive map lookup and returns 403 :No such channel
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

# Join channel #General
C1 SEND JOIN #General
C1 EXPECT 366 Alice #General :End of /NAMES list
C2 SEND JOIN #General
C1 WAIT_RECV :Bob!* JOIN #General

# C1 sends message using lowercase #general
C1 SEND PRIVMSG #general :Hello mixed case channel
C2 WAIT_RECV :Alice!* PRIVMSG #general :Hello mixed case channel
