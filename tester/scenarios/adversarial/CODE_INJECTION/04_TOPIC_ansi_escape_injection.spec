# 04_TOPIC_ansi_escape_injection.spec
# Vulnerability: Server accepts raw ANSI escape codes in TOPIC and relays them to channel members,
# allowing attackers to conceal logs, clear screens, or hijack recipient terminals.
# Expected secure behavior: Server must strip or reject ANSI control codes (e.g. \x1b[8m) from channel topics.
CLIENTS C1, C2

# Setup operator Alice
C1 SEND PASS 1234
C1 SEND NICK Ali031
C1 SEND USER ali031 0 * :Ali031 Usr031
C1 EXPECT 001 Ali031 :*

C1 SEND JOIN #inviszone
C1 WAIT_RECV :Ali031!* JOIN #inviszone

# Setup member Bob
C2 SEND PASS 1234
C2 SEND NICK Bob031
C2 SEND USER bob031 0 * :Bob031 Usr031
C2 EXPECT 001 Bob031 :*

C2 SEND JOIN #inviszone
C2 WAIT_RECV :Bob031!* JOIN #inviszone

# Alice attempts to set an ANSI conceal code in the channel topic
C1 SEND_RAW TOPIC #inviszone :\x1b[8mHiddenConcealedTopic\x1b[0m\r\n

# Secure server must either reject the topic or strip the ANSI codes so Bob does NOT receive raw ESC \x1b[8m
C2 WAIT_RECV :Ali031!* TOPIC #inviszone :HiddenConcealedTopic
