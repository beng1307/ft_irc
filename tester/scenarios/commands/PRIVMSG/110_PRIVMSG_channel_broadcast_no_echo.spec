# 110_PRIVMSG_channel_broadcast_no_echo.spec
# Tests channel broadcast echo suppression (sender does NOT receive their own channel message)
# Expected: C2 receives channel PRIVMSG, C1 receives no echo
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali295
C1 SEND USER ali295 0 * :Ali295
C1 EXPECT 001 Ali295 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob295
C2 SEND USER bob295 0 * :Bob295
C2 EXPECT 001 Bob295 :*

# Join channel #chan
C1 SEND JOIN #chan
C1 EXPECT 366 Ali295 #chan :End of /NAMES list
C2 SEND JOIN #chan
C1 WAIT_RECV :Bob295!* JOIN #chan

# C1 sends message to #chan
C1 SEND PRIVMSG #chan :Broadcast message
C2 WAIT_RECV :Ali295!* PRIVMSG #chan :Broadcast message
C1 NO_RECV :Ali295!* PRIVMSG #chan :Broadcast message
