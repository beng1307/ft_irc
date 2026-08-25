# 119_TOPIC_clear_topic_empty_colon.spec
# Tests clearing channel topic using trailing colon without text: TOPIC #chan :
# Expected: Server sets topic to empty string, broadcasts empty topic to members, and subsequent query yields 331 RPL_NOTOPIC.
CLIENTS C1, C2

# Alice creates channel and sets initial topic
C1 SEND PASS 1234
C1 SEND NICK Ali347
C1 SEND USER ali347 0 * :Ali347
C1 EXPECT 001 Ali347 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali347!* JOIN #lobby

# Bob joins channel
C2 SEND PASS 1234
C2 SEND NICK Bob347
C2 SEND USER bob347 0 * :Bob347
C2 EXPECT 001 Bob347 :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob347!* JOIN #lobby
C1 WAIT_RECV :Bob347!* JOIN #lobby

# Set initial topic
C1 SEND TOPIC #lobby :Initial Topic
C1 EXPECT :Ali347!* TOPIC #lobby :Initial Topic
C2 EXPECT :Ali347!* TOPIC #lobby :Initial Topic

# Alice clears topic
C1 SEND TOPIC #lobby :
C1 EXPECT :Ali347!* TOPIC #lobby :
C2 EXPECT :Ali347!* TOPIC #lobby :

# Bob queries topic, receives 331 No topic is set
C2 SEND TOPIC #lobby
C2 EXPECT 331 Bob347 #lobby :No topic is set
