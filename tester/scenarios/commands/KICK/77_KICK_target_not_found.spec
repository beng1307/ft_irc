# 77_KICK_target_not_found.spec
# Tests that an operator attempting to KICK a nonexistent nickname returns ERR_NOSUCHNICK (401).
CLIENTS C1

# Alice registers and creates #lobby77K
C1 SEND PASS 1234
C1 SEND NICK Ali132
C1 SEND USER ali132 0 * :Ali132
C1 EXPECT 001 Ali132 :*
C1 SEND JOIN #lobby77K
C1 EXPECT :Ali132!* JOIN #lobby77K

# Alice tries to kick a user that does not exist on the server
C1 SEND KICK #lobby77K GhostUser :reason
C1 EXPECT 401 Ali132 GhostUser :No such nick/channel
