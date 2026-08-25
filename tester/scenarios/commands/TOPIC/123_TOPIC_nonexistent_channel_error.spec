# 123_TOPIC_nonexistent_channel_error.spec
# Tests TOPIC on a non-existent channel
# Expected: Server replies with 403 ERR_NOSUCHCHANNEL
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali351
C1 SEND USER ali351 0 * :Ali351
C1 EXPECT 001 Ali351 :*

# Query non-existent channel
C1 SEND TOPIC #ghostchannel
C1 EXPECT 403 Ali351 #ghostchannel :No such channel

# Set non-existent channel
C1 SEND TOPIC #ghostchannel :Spooky Topic
C1 EXPECT 403 Ali351 #ghostchannel :No such channel
