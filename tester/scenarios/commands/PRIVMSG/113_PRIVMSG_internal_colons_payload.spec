# 113_PRIVMSG_internal_colons_payload.spec
# Tests PRIVMSG with multiple internal colons in message body
# Expected: Server preserves all colons inside the message body
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali298
C1 SEND USER ali298 0 * :Ali298
C1 EXPECT 001 Ali298 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob298
C2 SEND USER bob298 0 * :Bob298
C2 EXPECT 001 Bob298 :*

# Join channel #chan
C1 SEND JOIN #chan
C1 EXPECT 366 Ali298 #chan :End of /NAMES list
C2 SEND JOIN #chan
C1 WAIT_RECV :Bob298!* JOIN #chan

# C1 sends message with multiple internal colons
C1 SEND PRIVMSG #chan :Time is 12:34:56 and ::foo::bar
C2 WAIT_RECV :Ali298!* PRIVMSG #chan :Time is 12:34:56 and ::foo::bar
