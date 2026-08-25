# 107_PRIVMSG_no_such_channel_error.spec
# Tests PRIVMSG to a non-existent channel
# Expected: 403 ERR_NOSUCHCHANNEL (#ghost :No such channel)
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali292
C1 SEND USER ali292 0 * :Ali292
C1 EXPECT 001 Ali292 :*

# C1 sends message to non-existent channel
C1 SEND PRIVMSG #ghost :Hello?
C1 EXPECT 403 Ali292 #ghost :No such channel
