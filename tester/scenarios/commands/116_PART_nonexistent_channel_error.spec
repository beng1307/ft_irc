# 116_PART_nonexistent_channel_error.spec
# Tests ERR_NOSUCHCHANNEL (403) when attempting to part a channel that does not exist
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Attempt to part non-existent channel
C1 SEND PART #ghostchannel
C1 EXPECT 403 Alice #ghostchannel :No such channel
