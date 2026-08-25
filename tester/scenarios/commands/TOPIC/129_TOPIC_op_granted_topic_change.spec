# 129_TOPIC_op_granted_topic_change.spec
# Tests granting operator privileges (MODE +o) dynamically permits topic change in +t channel
# Expected: Once granted +o, user can successfully update topic in +t channel.
CLIENTS C1, C2

# Alice creates channel and enables +t
C1 SEND PASS 1234
C1 SEND NICK Ali357
C1 SEND USER ali357 0 * :Ali357
C1 EXPECT 001 Ali357 :*
C1 SEND JOIN #gated
C1 EXPECT :Ali357!* JOIN #gated
C1 SEND MODE #gated +t
C1 EXPECT :Ali357!* MODE #gated +t

# Bob joins
C2 SEND PASS 1234
C2 SEND NICK Bob357
C2 SEND USER bob357 0 * :Bob357
C2 EXPECT 001 Bob357 :*
C2 SEND JOIN #gated
C2 EXPECT :Bob357!* JOIN #gated
C1 WAIT_RECV :Bob357!* JOIN #gated

# Bob is initially rejected
C2 SEND TOPIC #gated :Bob357's First Attempt
C2 EXPECT 482 Bob357 #gated :You're not channel operator

# Alice promotes Bob to operator
C1 SEND MODE #gated +o Bob357
C1 EXPECT :Ali357!* MODE #gated +o Bob357
C2 EXPECT :Ali357!* MODE #gated +o Bob357

# Bob now succeeds in setting topic
C2 SEND TOPIC #gated :Bob357's Op Topic
C1 EXPECT :Bob357!* TOPIC #gated :Bob357's Op Topic
C2 EXPECT :Bob357!* TOPIC #gated :Bob357's Op Topic
