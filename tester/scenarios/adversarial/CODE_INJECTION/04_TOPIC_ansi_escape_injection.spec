# 04_TOPIC_ansi_escape_injection.spec
# Vulnerability: Server accepts raw ANSI escape codes in TOPIC and relays them to channel members,
# allowing attackers to conceal logs, clear screens, or hijack recipient terminals.
# Expected secure behavior: Server must strip or reject ANSI control codes (e.g. \x1b[8m) from channel topics.
CLIENTS C1, C2

# Setup operator Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice User
C1 EXPECT 001 Alice :*

C1 SEND JOIN #inviszone
C1 WAIT_RECV :Alice!* JOIN #inviszone

# Setup member Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob User
C2 EXPECT 001 Bob :*

C2 SEND JOIN #inviszone
C2 WAIT_RECV :Bob!* JOIN #inviszone

# Alice attempts to set an ANSI conceal code in the channel topic
C1 SEND_RAW TOPIC #inviszone :\x1b[8mHiddenConcealedTopic\x1b[0m\r\n

# Secure server must either reject the topic or strip the ANSI codes so Bob does NOT receive raw ESC \x1b[8m
C2 WAIT_RECV :Alice!* TOPIC #inviszone :HiddenConcealedTopic
