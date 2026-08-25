# 132_TOPIC_whitespace_preservation.spec
# Tests that leading and internal whitespace in topic parameter is preserved
# Expected: Topic includes leading space after colon.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali360
C1 SEND USER ali360 0 * :Ali360
C1 EXPECT 001 Ali360 :*
C1 SEND JOIN #room
C1 EXPECT :Ali360!* JOIN #room

# Alice sets topic with leading space
C1 SEND TOPIC #room :  Indented Topic Content
C1 EXPECT :Ali360!* TOPIC #room :  Indented Topic Content

# Query topic
C1 SEND TOPIC #room
C1 EXPECT 332 Ali360 #room :  Indented Topic Content
