# 136_TOPIC_channel_destruction_resets_topic.spec
# Tests that when all members leave a channel, the channel is destroyed and its topic is cleared for future creations
# Expected: A newly created channel after previous incarnation died has no topic (331 RPL_NOTOPIC).
CLIENTS C1, C2

# Alice creates #ephemeral, sets topic, then leaves
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #ephemeral
C1 EXPECT :Alice!* JOIN #ephemeral
C1 SEND TOPIC #ephemeral :Secret Topic of Dead Channel
C1 EXPECT :Alice!* TOPIC #ephemeral :Secret Topic of Dead Channel

# Alice parts -> channel is now empty and destroyed
C1 SEND PART #ephemeral :Goodbye
C1 EXPECT :Alice!* PART #ephemeral :Goodbye

# Bob connects and creates #ephemeral from scratch
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #ephemeral
C2 EXPECT :Bob!* JOIN #ephemeral

# Bob queries topic -> should NOT leak Alice's old topic
C2 SEND TOPIC #ephemeral
C2 EXPECT 331 Bob #ephemeral :No topic is set
