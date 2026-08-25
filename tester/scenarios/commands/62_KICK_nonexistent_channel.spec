# 62_KICK_nonexistent_channel.spec
# Tests that KICK on a channel that does not exist returns ERR_NOSUCHCHANNEL (403).
CLIENTS C1

# Register Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Attempt to kick from a nonexistent channel
C1 SEND KICK #GhostChannel Bob :get out
C1 EXPECT 403 Alice #GhostChannel :No such channel
