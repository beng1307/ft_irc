# 100_PRIVMSG_case_insensitive_nick.spec
# Tests RFC 2812 case-insensitivity when addressing users via PRIVMSG
# Expected: PRIVMSG BOB reaches user registered as 'Bob'
# Bug: Server performs case-sensitive nickname matching and returns 401 ERR_NOSUCHNICK
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2 registered as 'Bob'
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 sends message to uppercase 'BOB'
C1 SEND PRIVMSG BOB :Hello Bob
C2 WAIT_RECV :Alice!* PRIVMSG BOB :Hello Bob
