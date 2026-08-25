# 125_TOPIC_unrestricted_channel_regular_member.spec
# Tests that in an unrestricted channel (-t), a regular non-operator member can change the topic
# Expected: Server accepts topic change from regular member and broadcasts to all channel members.
CLIENTS C1, C2

# Alice creates channel (starts as -t by default)
C1 SEND PASS 1234
C1 SEND NICK Ali353
C1 SEND USER ali353 0 * :Ali353
C1 EXPECT 001 Ali353 :*
C1 SEND JOIN #openroom
C1 EXPECT :Ali353!* JOIN #openroom

# Bob joins channel as regular member
C2 SEND PASS 1234
C2 SEND NICK Bob353
C2 SEND USER bob353 0 * :Bob353
C2 EXPECT 001 Bob353 :*
C2 SEND JOIN #openroom
C2 EXPECT :Bob353!* JOIN #openroom
C1 WAIT_RECV :Bob353!* JOIN #openroom

# Bob (non-op) sets topic in unrestricted channel
C2 SEND TOPIC #openroom :Bob353's Free Topic
C1 EXPECT :Bob353!* TOPIC #openroom :Bob353's Free Topic
C2 EXPECT :Bob353!* TOPIC #openroom :Bob353's Free Topic

# Alice queries topic
C1 SEND TOPIC #openroom
C1 EXPECT 332 Ali353 #openroom :Bob353's Free Topic
