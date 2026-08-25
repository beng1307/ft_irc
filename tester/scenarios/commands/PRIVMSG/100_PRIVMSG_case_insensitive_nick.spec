# 100_PRIVMSG_case_insensitive_nick.spec
# Tests RFC 2812 case-insensitivity when addressing users via PRIVMSG
# Expected: PRIVMSG BOB reaches user registered as 'Bob'
# Bug: Server performs case-sensitive nickname matching and returns 401 ERR_NOSUCHNICK
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali285
C1 SEND USER ali285 0 * :Ali285
C1 EXPECT 001 Ali285 :*

# Setup C2 registered as 'Bob'
C2 SEND PASS 1234
C2 SEND NICK Bob285
C2 SEND USER bob285 0 * :Bob285
C2 EXPECT 001 Bob285 :*

# C1 sends message to uppercase 'BOB'
C1 SEND PRIVMSG BOB :Hello Bob285
C2 WAIT_RECV :Ali285!* PRIVMSG BOB :Hello Bob285
