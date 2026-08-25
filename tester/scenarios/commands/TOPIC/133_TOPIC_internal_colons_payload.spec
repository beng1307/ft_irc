# 133_TOPIC_internal_colons_payload.spec
# Tests that multiple internal colons in the topic string are preserved intact
# Expected: Server does not truncate or split on subsequent colons in topic payload.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali361
C1 SEND USER ali361 0 * :Ali361
C1 EXPECT 001 Ali361 :*
C1 SEND JOIN #dev
C1 EXPECT :Ali361!* JOIN #dev

C2 SEND PASS 1234
C2 SEND NICK Bob361
C2 SEND USER bob361 0 * :Bob361
C2 EXPECT 001 Bob361 :*
C2 SEND JOIN #dev
C2 EXPECT :Bob361!* JOIN #dev
C1 WAIT_RECV :Bob361!* JOIN #dev

# Alice sets topic with multiple internal colons
C1 SEND TOPIC #dev :Section 1: General : Section 2: Important : Section 3: Notes
C1 EXPECT :Ali361!* TOPIC #dev :Section 1: General : Section 2: Important : Section 3: Notes
C2 EXPECT :Ali361!* TOPIC #dev :Section 1: General : Section 2: Important : Section 3: Notes

# Bob queries topic
C2 SEND TOPIC #dev
C2 EXPECT 332 Bob361 #dev :Section 1: General : Section 2: Important : Section 3: Notes
