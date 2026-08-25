# Tests TOPIC clearing (:), topic query when not on channel (442), and non-existent channel (403).
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali042
C1 SEND USER ali042 0 * :Ali042
C1 EXPECT 001 Ali042 :*

C2 SEND PASS 1234
C2 SEND NICK Bob042
C2 SEND USER bob042 0 * :Bob042
C2 EXPECT 001 Bob042 :*

# TOPIC-08: TOPIC on non-existent channel
C1 SEND TOPIC #nonexistent
C1 EXPECT 403 Ali042 #nonexistent :*

# C1 creates channel and sets initial topic
C1 SEND JOIN #topictest
C1 EXPECT :Ali042!* JOIN #topictest
C1 SEND TOPIC #topictest :Initial Topic
C1 EXPECT :Ali042!* TOPIC #topictest :Initial Topic

# TOPIC-07: Bob (not in channel) queries or attempts to set topic
C2 SEND TOPIC #topictest
C2 EXPECT 442 Bob042 #topictest :*

# Bob joins channel and queries topic
C2 SEND JOIN #topictest
C2 WAIT_RECV :Bob042!* JOIN #topictest
C1 WAIT_RECV :Bob042!* JOIN #topictest
C2 SEND TOPIC #topictest
C2 EXPECT 332 Bob042 #topictest :Initial Topic

# TOPIC-06: Operator Alice clears topic by sending empty trailing ':'
C1 SEND TOPIC #topictest :
C2 WAIT_RECV :Ali042!* TOPIC #topictest :*

# Verify subsequent TOPIC query returns 331 RPL_NOTOPIC
C2 SEND TOPIC #topictest
C2 EXPECT 331 Bob042 #topictest :*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
