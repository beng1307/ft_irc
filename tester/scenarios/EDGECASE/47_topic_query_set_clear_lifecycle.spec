# Scenario 47: Topic Query, Set, and Clear Lifecycle
# Tests querying empty topic (331), setting topic, querying set topic (332), and clearing topic
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates #topictest
C1 SEND JOIN #topictest
C1 EXPECT :Alice!* JOIN #topictest

# Query topic when unset -> 331
C1 SEND TOPIC #topictest
C1 EXPECT 331 Alice #topictest :*

# Set topic
C1 SEND TOPIC #topictest :Initial Cool Topic
C1 EXPECT :Alice!* TOPIC #topictest :Initial Cool Topic

# Bob joins and queries topic -> 332
C2 SEND JOIN #topictest
C2 WAIT_RECV :Bob!* JOIN #topictest
C2 SEND TOPIC #topictest
C2 EXPECT 332 Bob #topictest :Initial Cool Topic

# Alice clears topic
C1 SEND TOPIC #topictest :
C1 EXPECT :Alice!* TOPIC #topictest :
C2 WAIT_RECV :Alice!* TOPIC #topictest :

# Query topic after clearing -> 331
C2 SEND TOPIC #topictest
C2 EXPECT 331 Bob #topictest :*
