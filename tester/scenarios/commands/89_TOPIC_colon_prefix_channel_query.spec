# 89_TOPIC_colon_prefix_channel_query.spec
# Tests RFC 1459/2812 colon prefix on target channel parameter: TOPIC :#chan
# Expected: Server strips leading colon and queries topic for #chan (returns 331 RPL_NOTOPIC).
# Bug: Server treats channel as ':#chan' literally and fails with 403 :#chan :No such channel.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Alice queries topic using colon-prefixed channel name
C1 SEND TOPIC :#lobby
C1 EXPECT 331 Alice #lobby :No topic is set
