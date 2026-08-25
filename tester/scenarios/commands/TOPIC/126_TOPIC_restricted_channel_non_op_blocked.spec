# 126_TOPIC_restricted_channel_non_op_blocked.spec
# Tests that in a topic-restricted channel (+t), non-operators cannot change the topic
# Expected: Server replies with 482 ERR_CHANOPRIVSNEEDED and topic remains unchanged.
CLIENTS C1, C2

# Alice creates channel and enables +t
C1 SEND PASS 1234
C1 SEND NICK Ali354
C1 SEND USER ali354 0 * :Ali354
C1 EXPECT 001 Ali354 :*
C1 SEND JOIN #restricted
C1 EXPECT :Ali354!* JOIN #restricted
C1 SEND MODE #restricted +t
C1 EXPECT :Ali354!* MODE #restricted +t
C1 SEND TOPIC #restricted :Official Op Topic
C1 EXPECT :Ali354!* TOPIC #restricted :Official Op Topic

# Bob joins channel as regular member
C2 SEND PASS 1234
C2 SEND NICK Bob354
C2 SEND USER bob354 0 * :Bob354
C2 EXPECT 001 Bob354 :*
C2 SEND JOIN #restricted
C2 EXPECT :Bob354!* JOIN #restricted
C1 WAIT_RECV :Bob354!* JOIN #restricted

# Bob attempts to change topic
C2 SEND TOPIC #restricted :Bob354's Unauthorized Topic
C2 EXPECT 482 Bob354 #restricted :You're not channel operator

# Verify topic was not changed
C2 SEND TOPIC #restricted
C2 EXPECT 332 Bob354 #restricted :Official Op Topic
