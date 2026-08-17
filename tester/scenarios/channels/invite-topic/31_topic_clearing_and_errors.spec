# Tests TOPIC clearing (:), topic query when not on channel (442), and non-existent channel (403).
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# TOPIC-08: TOPIC on non-existent channel
C1 SEND TOPIC #nonexistent
C1 EXPECT 403 Alice #nonexistent :*

# C1 creates channel and sets initial topic
C1 SEND JOIN #topictest
C1 EXPECT :Alice!* JOIN #topictest
C1 SEND TOPIC #topictest :Initial Topic
C1 EXPECT :Alice!* TOPIC #topictest :Initial Topic

# TOPIC-07: Bob (not in channel) queries or attempts to set topic
C2 SEND TOPIC #topictest
C2 EXPECT 442 Bob #topictest :*

# Bob joins channel and queries topic
C2 SEND JOIN #topictest
C2 WAIT_RECV :Bob!* JOIN #topictest
C1 WAIT_RECV :Bob!* JOIN #topictest
C2 SEND TOPIC #topictest
C2 EXPECT 332 Bob #topictest :Initial Topic

# TOPIC-06: Operator Alice clears topic by sending empty trailing ':'
C1 SEND TOPIC #topictest :
C2 WAIT_RECV :Alice!* TOPIC #topictest :*

# Verify subsequent TOPIC query returns 331 RPL_NOTOPIC
C2 SEND TOPIC #topictest
C2 EXPECT 331 Bob #topictest :*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
