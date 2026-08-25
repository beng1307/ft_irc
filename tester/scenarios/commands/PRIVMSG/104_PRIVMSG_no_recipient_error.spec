# 104_PRIVMSG_no_recipient_error.spec
# Tests PRIVMSG with missing recipient parameter
# Expected: 411 ERR_NORECIPIENT (:No recipient given (PRIVMSG))
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali289
C1 SEND USER ali289 0 * :Ali289
C1 EXPECT 001 Ali289 :*

# C1 sends PRIVMSG without recipient
C1 SEND PRIVMSG
C1 EXPECT 411 Ali289 :No recipient given (PRIVMSG)
