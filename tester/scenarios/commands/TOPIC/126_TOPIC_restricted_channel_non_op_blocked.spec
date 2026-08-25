# 126_TOPIC_restricted_channel_non_op_blocked.spec
# Tests that in a topic-restricted channel (+t), non-operators cannot change the topic
# Expected: Server replies with 482 ERR_CHANOPRIVSNEEDED and topic remains unchanged.
CLIENTS C1, C2

# Alice creates channel and enables +t
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #restricted
C1 EXPECT :Alice!* JOIN #restricted
C1 SEND MODE #restricted +t
C1 EXPECT :Alice!* MODE #restricted +t
C1 SEND TOPIC #restricted :Official Op Topic
C1 EXPECT :Alice!* TOPIC #restricted :Official Op Topic

# Bob joins channel as regular member
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #restricted
C2 EXPECT :Bob!* JOIN #restricted
C1 WAIT_RECV :Bob!* JOIN #restricted

# Bob attempts to change topic
C2 SEND TOPIC #restricted :Bob's Unauthorized Topic
C2 EXPECT 482 Bob #restricted :You're not channel operator

# Verify topic was not changed
C2 SEND TOPIC #restricted
C2 EXPECT 332 Bob #restricted :Official Op Topic
