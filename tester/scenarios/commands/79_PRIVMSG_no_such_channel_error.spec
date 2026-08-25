# 49_PRIVMSG_no_such_channel_error.spec
# Tests PRIVMSG to a non-existent channel
# Expected: 403 ERR_NOSUCHCHANNEL (#ghost :No such channel)
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C1 sends message to non-existent channel
C1 SEND PRIVMSG #ghost :Hello?
C1 EXPECT 403 Alice #ghost :No such channel
