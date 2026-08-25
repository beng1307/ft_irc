# 117_TOPIC_colon_prefix_channel_query.spec
# Tests RFC 1459/2812 colon prefix on target channel parameter: TOPIC :#chan
# Expected: Server strips leading colon and queries topic for #chan (returns 331 RPL_NOTOPIC).
# Bug: Server treats channel as ':#chan' literally and fails with 403 :#chan :No such channel.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali345
C1 SEND USER ali345 0 * :Ali345
C1 EXPECT 001 Ali345 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali345!* JOIN #lobby

# Alice queries topic using colon-prefixed channel name
C1 SEND TOPIC :#lobby
C1 EXPECT 331 Ali345 #lobby :No topic is set
