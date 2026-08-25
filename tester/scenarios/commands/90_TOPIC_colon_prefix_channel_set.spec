# 90_TOPIC_colon_prefix_channel_set.spec
# Tests colon-prefixed channel name when setting topic: TOPIC :#chan :New Topic
# Expected: Server sets topic for #chan and broadcasts to channel members.
# Bug: Server treats channel as ':#chan' literally and fails with 403 :#chan :No such channel.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Alice sets topic with colon prefix on channel parameter
C1 SEND TOPIC :#lobby :New Topic
C1 EXPECT :Alice!* TOPIC #lobby :New Topic
