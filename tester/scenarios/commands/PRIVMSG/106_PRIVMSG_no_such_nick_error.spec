# 106_PRIVMSG_no_such_nick_error.spec
# Tests PRIVMSG to a non-existent user
# Expected: 401 ERR_NOSUCHNICK (NonExistent :No such nick/channel)
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali291
C1 SEND USER ali291 0 * :Ali291
C1 EXPECT 001 Ali291 :*

# C1 sends message to non-existent nick
C1 SEND PRIVMSG GhostUser :Are you there?
C1 EXPECT 401 Ali291 GhostUser :No such nick/channel
