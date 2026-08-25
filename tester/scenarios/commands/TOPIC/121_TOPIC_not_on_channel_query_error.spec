# 121_TOPIC_not_on_channel_query_error.spec
# Tests TOPIC query when client is not a member of the channel
# Expected: Server replies with 442 ERR_NOTONCHANNEL
CLIENTS C1, C2

# Alice creates #privatechan
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #privatechan
C1 EXPECT :Alice!* JOIN #privatechan

# Bob connects but does NOT join #privatechan
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Bob attempts to query topic of #privatechan
C2 SEND TOPIC #privatechan
C2 EXPECT 442 Bob #privatechan :You're not on that channel
