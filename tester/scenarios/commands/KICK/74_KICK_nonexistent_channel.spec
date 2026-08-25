# 74_KICK_nonexistent_channel.spec
# Tests that KICK on a channel that does not exist returns ERR_NOSUCHCHANNEL (403).
CLIENTS C1

# Register Alice
C1 SEND PASS 1234
C1 SEND NICK Ali129
C1 SEND USER ali129 0 * :Ali129
C1 EXPECT 001 Ali129 :*

# Attempt to kick from a nonexistent channel
C1 SEND KICK #GhostChannel Bob129 :get out
C1 EXPECT 403 Ali129 #GhostChannel :No such channel
