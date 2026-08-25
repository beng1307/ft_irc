# 121_TOPIC_not_on_channel_query_error.spec
# Tests TOPIC query when client is not a member of the channel
# Expected: Server replies with 442 ERR_NOTONCHANNEL
CLIENTS C1, C2

# Alice creates #privatechan
C1 SEND PASS 1234
C1 SEND NICK Ali349
C1 SEND USER ali349 0 * :Ali349
C1 EXPECT 001 Ali349 :*
C1 SEND JOIN #privatechan
C1 EXPECT :Ali349!* JOIN #privatechan

# Bob connects but does NOT join #privatechan
C2 SEND PASS 1234
C2 SEND NICK Bob349
C2 SEND USER bob349 0 * :Bob349
C2 EXPECT 001 Bob349 :*

# Bob attempts to query topic of #privatechan
C2 SEND TOPIC #privatechan
C2 EXPECT 442 Bob349 #privatechan :You're not on that channel
