# 91_TOPIC_clear_topic_empty_colon.spec
# Tests clearing channel topic using trailing colon without text: TOPIC #chan :
# Expected: Server sets topic to empty string, broadcasts empty topic to members, and subsequent query yields 331 RPL_NOTOPIC.
CLIENTS C1, C2

# Alice creates channel and sets initial topic
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob joins channel
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Set initial topic
C1 SEND TOPIC #lobby :Initial Topic
C1 EXPECT :Alice!* TOPIC #lobby :Initial Topic
C2 EXPECT :Alice!* TOPIC #lobby :Initial Topic

# Alice clears topic
C1 SEND TOPIC #lobby :
C1 EXPECT :Alice!* TOPIC #lobby :
C2 EXPECT :Alice!* TOPIC #lobby :

# Bob queries topic, receives 331 No topic is set
C2 SEND TOPIC #lobby
C2 EXPECT 331 Bob #lobby :No topic is set
