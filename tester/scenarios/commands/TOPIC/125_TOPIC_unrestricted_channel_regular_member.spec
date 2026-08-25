# 125_TOPIC_unrestricted_channel_regular_member.spec
# Tests that in an unrestricted channel (-t), a regular non-operator member can change the topic
# Expected: Server accepts topic change from regular member and broadcasts to all channel members.
CLIENTS C1, C2

# Alice creates channel (starts as -t by default)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #openroom
C1 EXPECT :Alice!* JOIN #openroom

# Bob joins channel as regular member
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #openroom
C2 EXPECT :Bob!* JOIN #openroom
C1 WAIT_RECV :Bob!* JOIN #openroom

# Bob (non-op) sets topic in unrestricted channel
C2 SEND TOPIC #openroom :Bob's Free Topic
C1 EXPECT :Bob!* TOPIC #openroom :Bob's Free Topic
C2 EXPECT :Bob!* TOPIC #openroom :Bob's Free Topic

# Alice queries topic
C1 SEND TOPIC #openroom
C1 EXPECT 332 Alice #openroom :Bob's Free Topic
