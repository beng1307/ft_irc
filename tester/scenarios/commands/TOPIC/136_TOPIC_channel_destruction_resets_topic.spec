# 136_TOPIC_channel_destruction_resets_topic.spec
# Tests that when all members leave a channel, the channel is destroyed and its topic is cleared for future creations
# Expected: A newly created channel after previous incarnation died has no topic (331 RPL_NOTOPIC).
CLIENTS C1, C2

# Alice creates #ephemeral, sets topic, then leaves
C1 SEND PASS 1234
C1 SEND NICK Ali364
C1 SEND USER ali364 0 * :Ali364
C1 EXPECT 001 Ali364 :*
C1 SEND JOIN #ephemeral
C1 EXPECT :Ali364!* JOIN #ephemeral
C1 SEND TOPIC #ephemeral :Secret Topic of Dead Channel
C1 EXPECT :Ali364!* TOPIC #ephemeral :Secret Topic of Dead Channel

# Alice parts -> channel is now empty and destroyed
C1 SEND PART #ephemeral :Goodbye
C1 EXPECT :Ali364!* PART #ephemeral :Goodbye

# Bob connects and creates #ephemeral from scratch
C2 SEND PASS 1234
C2 SEND NICK Bob364
C2 SEND USER bob364 0 * :Bob364
C2 EXPECT 001 Bob364 :*
C2 SEND JOIN #ephemeral
C2 EXPECT :Bob364!* JOIN #ephemeral

# Bob queries topic -> should NOT leak Alice's old topic
C2 SEND TOPIC #ephemeral
C2 EXPECT 331 Bob364 #ephemeral :No topic is set
