# Scenario 47: Topic Query, Set, and Clear Lifecycle
# Tests querying empty topic (331), setting topic, querying set topic (332), and clearing topic
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali009
C1 SEND USER ali009 0 * :Ali009
C1 EXPECT 001 Ali009 :*

C2 SEND PASS 1234
C2 SEND NICK Bob009
C2 SEND USER bob009 0 * :Bob009
C2 EXPECT 001 Bob009 :*

# Alice creates #topictest
C1 SEND JOIN #topictest
C1 EXPECT :Ali009!* JOIN #topictest

# Query topic when unset -> 331
C1 SEND TOPIC #topictest
C1 EXPECT 331 Ali009 #topictest :*

# Set topic
C1 SEND TOPIC #topictest :Initial Cool Topic
C1 EXPECT :Ali009!* TOPIC #topictest :Initial Cool Topic

# Bob joins and queries topic -> 332
C2 SEND JOIN #topictest
C2 WAIT_RECV :Bob009!* JOIN #topictest
C2 SEND TOPIC #topictest
C2 EXPECT 332 Bob009 #topictest :Initial Cool Topic

# Alice clears topic
C1 SEND TOPIC #topictest :
C1 EXPECT :Ali009!* TOPIC #topictest :
C2 WAIT_RECV :Ali009!* TOPIC #topictest :

# Query topic after clearing -> 331
C2 SEND TOPIC #topictest
C2 EXPECT 331 Bob009 #topictest :*
