# 114_PRIVMSG_mode_restriction_isolation.spec
# Tests that channel modes (+t, +i, +k, +l) do NOT block member PRIVMSG exchanges
# Expected: Existing channel members can chat freely despite active channel modes
CLIENTS C1, C2

# Setup C1 (Operator)
C1 SEND PASS 1234
C1 SEND NICK Ali299
C1 SEND USER ali299 0 * :Ali299
C1 EXPECT 001 Ali299 :*

# Setup C2 (Regular Member)
C2 SEND PASS 1234
C2 SEND NICK Bob299
C2 SEND USER bob299 0 * :Bob299
C2 EXPECT 001 Bob299 :*

# Join channel #modetest
C1 SEND JOIN #modetest
C1 EXPECT 366 Ali299 #modetest :End of /NAMES list
C2 SEND JOIN #modetest
C1 WAIT_RECV :Bob299!* JOIN #modetest

# C1 enables modes +t +i +k secret +l 1
C1 SEND MODE #modetest +tikl secret 1
C1 WAIT_RECV :Ali299!* MODE #modetest +tikl secret 1


# C2 (non-op) sends PRIVMSG to channel
C2 SEND PRIVMSG #modetest :Still able to talk
C1 WAIT_RECV :Bob299!* PRIVMSG #modetest :Still able to talk
