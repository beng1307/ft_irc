# 129_TOPIC_op_granted_topic_change.spec
# Tests granting operator privileges (MODE +o) dynamically permits topic change in +t channel
# Expected: Once granted +o, user can successfully update topic in +t channel.
CLIENTS C1, C2

# Alice creates channel and enables +t
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #gated
C1 EXPECT :Alice!* JOIN #gated
C1 SEND MODE #gated +t
C1 EXPECT :Alice!* MODE #gated +t

# Bob joins
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #gated
C2 EXPECT :Bob!* JOIN #gated
C1 WAIT_RECV :Bob!* JOIN #gated

# Bob is initially rejected
C2 SEND TOPIC #gated :Bob's First Attempt
C2 EXPECT 482 Bob #gated :You're not channel operator

# Alice promotes Bob to operator
C1 SEND MODE #gated +o Bob
C1 EXPECT :Alice!* MODE #gated +o Bob
C2 EXPECT :Alice!* MODE #gated +o Bob

# Bob now succeeds in setting topic
C2 SEND TOPIC #gated :Bob's Op Topic
C1 EXPECT :Bob!* TOPIC #gated :Bob's Op Topic
C2 EXPECT :Bob!* TOPIC #gated :Bob's Op Topic
