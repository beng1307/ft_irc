# 267_TOPIC_quad_colons_leading_payload.spec
# Tests adversarial payload with quad leading colons: TOPIC #chan ::::LeadingColons
# Expected: Server consumes the first colon as parameter delimiter, preserving the remaining three colons in the stored topic.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali368
C1 SEND USER ali368 0 * :Ali368
C1 EXPECT 001 Ali368 :*
C1 SEND JOIN #lobby267T
C1 EXPECT :Ali368!* JOIN #lobby267T

C2 SEND PASS 1234
C2 SEND NICK Bob368
C2 SEND USER bob368 0 * :Bob368
C2 EXPECT 001 Bob368 :*
C2 SEND JOIN #lobby267T
C2 EXPECT :Bob368!* JOIN #lobby267T
C1 WAIT_RECV :Bob368!* JOIN #lobby267T

# Alice sets quad-colon topic
C1 SEND TOPIC #lobby267T ::::QuadColonTopic
C1 EXPECT :Ali368!* TOPIC #lobby267T ::::QuadColonTopic
C2 EXPECT :Ali368!* TOPIC #lobby267T ::::QuadColonTopic

# Bob queries topic
C2 SEND TOPIC #lobby267T
C2 EXPECT 332 Bob368 #lobby267T ::::QuadColonTopic
