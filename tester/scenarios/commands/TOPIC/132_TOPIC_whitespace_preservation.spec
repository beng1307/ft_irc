# 132_TOPIC_whitespace_preservation.spec
# Tests that leading and internal whitespace in topic parameter is preserved
# Expected: Topic includes leading space after colon.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #room
C1 EXPECT :Alice!* JOIN #room

# Alice sets topic with leading space
C1 SEND TOPIC #room :  Indented Topic Content
C1 EXPECT :Alice!* TOPIC #room :  Indented Topic Content

# Query topic
C1 SEND TOPIC #room
C1 EXPECT 332 Alice #room :  Indented Topic Content
