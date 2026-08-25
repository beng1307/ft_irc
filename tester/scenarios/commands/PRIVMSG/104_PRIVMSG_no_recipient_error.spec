# 104_PRIVMSG_no_recipient_error.spec
# Tests PRIVMSG with missing recipient parameter
# Expected: 411 ERR_NORECIPIENT (:No recipient given (PRIVMSG))
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C1 sends PRIVMSG without recipient
C1 SEND PRIVMSG
C1 EXPECT 411 Alice :No recipient given (PRIVMSG)
