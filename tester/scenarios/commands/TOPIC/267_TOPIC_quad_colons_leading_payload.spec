# 267_TOPIC_quad_colons_leading_payload.spec
# Tests adversarial payload with quad leading colons: TOPIC #chan ::::LeadingColons
# Expected: Server consumes the first colon as parameter delimiter, preserving the remaining three colons in the stored topic.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice sets quad-colon topic
C1 SEND TOPIC #lobby ::::QuadColonTopic
C1 EXPECT :Alice!* TOPIC #lobby ::::QuadColonTopic
C2 EXPECT :Alice!* TOPIC #lobby ::::QuadColonTopic

# Bob queries topic
C2 SEND TOPIC #lobby
C2 EXPECT 332 Bob #lobby ::::QuadColonTopic
