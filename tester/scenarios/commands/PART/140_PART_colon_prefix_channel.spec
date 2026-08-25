# 140_PART_colon_prefix_channel.spec
# Tests RFC 2812 §2.3.1 colon prefix on single channel parameter: PART :#lobby140P :Goodbye
# Expected: Server parses :#lobby140P as target channel #lobby140P and successfully parts client.
# Bug: Server treats ':#lobby140P' literally without stripping prefix colon, querying non-existent channel ':#lobby140P' and returning 403.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali209
C1 SEND USER ali209 0 * :Ali209
C1 EXPECT 001 Ali209 :*
C1 SEND JOIN #lobby140P
C1 EXPECT :Ali209!* JOIN #lobby140P

# Part with colon prefix on channel name
C1 SEND PART :#lobby140P :Goodbye
C1 EXPECT :Ali209!* PART #lobby140P :Goodbye
