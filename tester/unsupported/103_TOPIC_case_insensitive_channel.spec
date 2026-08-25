# 103_TOPIC_case_insensitive_channel.spec
# Tests RFC 2812 case-insensitivity of channel names during TOPIC query
# Expected: Server normalizes channel name and returns topic for #mychannel when queried as #MYCHANNEL.
# Bug: Server stores channels in case-sensitive Map and returns 403 #MYCHANNEL :No such channel.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #mychannel
C1 EXPECT :Alice!* JOIN #mychannel
C1 SEND TOPIC #mychannel :General Discussion
C1 EXPECT :Alice!* TOPIC #mychannel :General Discussion

# Query with uppercase channel name
C1 SEND TOPIC #MYCHANNEL
C1 EXPECT 332 Alice #MYCHANNEL :General Discussion
