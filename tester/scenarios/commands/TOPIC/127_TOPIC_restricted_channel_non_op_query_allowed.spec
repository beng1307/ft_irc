# 127_TOPIC_restricted_channel_non_op_query_allowed.spec
# Tests that topic query is permitted for non-operators in a +t restricted channel
# Expected: Server replies with 332 RPL_TOPIC containing the current topic.
CLIENTS C1, C2

# Alice creates channel, sets +t, and sets topic
C1 SEND PASS 1234
C1 SEND NICK Ali355
C1 SEND USER ali355 0 * :Ali355
C1 EXPECT 001 Ali355 :*
C1 SEND JOIN #restricted
C1 EXPECT :Ali355!* JOIN #restricted
C1 SEND MODE #restricted +t
C1 EXPECT :Ali355!* MODE #restricted +t
C1 SEND TOPIC #restricted :Top Secret Notice
C1 EXPECT :Ali355!* TOPIC #restricted :Top Secret Notice

# Bob joins channel
C2 SEND PASS 1234
C2 SEND NICK Bob355
C2 SEND USER bob355 0 * :Bob355
C2 EXPECT 001 Bob355 :*
C2 SEND JOIN #restricted
C2 EXPECT :Bob355!* JOIN #restricted
C1 WAIT_RECV :Bob355!* JOIN #restricted

# Bob queries topic in +t channel
C2 SEND TOPIC #restricted
C2 EXPECT 332 Bob355 #restricted :Top Secret Notice
