# 131_TOPIC_case_insensitive_channel.spec
# Tests RFC 2812 case-insensitivity of channel names during TOPIC query
# Expected: Server normalizes channel name and returns topic for #mychannel when queried as #MYCHANNEL.
# Bug: Server stores channels in case-sensitive Map and returns 403 #MYCHANNEL :No such channel.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali359
C1 SEND USER ali359 0 * :Ali359
C1 EXPECT 001 Ali359 :*
C1 SEND JOIN #mychannel
C1 EXPECT :Ali359!* JOIN #mychannel
C1 SEND TOPIC #mychannel :General Discussion
C1 EXPECT :Ali359!* TOPIC #mychannel :General Discussion

# Query with uppercase channel name
C1 SEND TOPIC #MYCHANNEL
C1 EXPECT 332 Ali359 #MYCHANNEL :General Discussion
