# 112_PRIVMSG_whitespace_only_payload.spec
# Tests PRIVMSG with whitespace-only payload
# Expected: Whitespace message delivered intact to recipient
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali297
C1 SEND USER ali297 0 * :Ali297
C1 EXPECT 001 Ali297 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob297
C2 SEND USER bob297 0 * :Bob297
C2 EXPECT 001 Bob297 :*

# Join channel #chan
C1 SEND JOIN #chan
C1 EXPECT 366 Ali297 #chan :End of /NAMES list
C2 SEND JOIN #chan
C1 WAIT_RECV :Bob297!* JOIN #chan

# C1 sends whitespace payload
C1 SEND_RAW PRIVMSG #chan :   \r\n
C2 WAIT_RECV :Ali297!* PRIVMSG #chan :   
