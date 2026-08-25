# 144_PART_nonexistent_channel_error.spec
# Tests ERR_NOSUCHCHANNEL (403) when attempting to part a channel that does not exist
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali213
C1 SEND USER ali213 0 * :Ali213
C1 EXPECT 001 Ali213 :*

# Attempt to part non-existent channel
C1 SEND PART #ghostchannel
C1 EXPECT 403 Ali213 #ghostchannel :No such channel
