# 106_PRIVMSG_no_such_nick_error.spec
# Tests PRIVMSG to a non-existent user
# Expected: 401 ERR_NOSUCHNICK (NonExistent :No such nick/channel)
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C1 sends message to non-existent nick
C1 SEND PRIVMSG GhostUser :Are you there?
C1 EXPECT 401 Alice GhostUser :No such nick/channel
