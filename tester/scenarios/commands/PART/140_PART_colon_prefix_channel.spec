# 140_PART_colon_prefix_channel.spec
# Tests RFC 2812 §2.3.1 colon prefix on single channel parameter: PART :#lobby :Goodbye
# Expected: Server parses :#lobby as target channel #lobby and successfully parts client.
# Bug: Server treats ':#lobby' literally without stripping prefix colon, querying non-existent channel ':#lobby' and returning 403.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali209
C1 SEND USER ali209 0 * :Ali209
C1 EXPECT 001 Ali209 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali209!* JOIN #lobby

# Part with colon prefix on channel name
C1 SEND PART :#lobby :Goodbye
C1 EXPECT :Ali209!* PART #lobby :Goodbye
