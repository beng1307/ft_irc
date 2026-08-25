# 137_TOPIC_nick_change_broadcaster_prefix.spec
# Tests that when a user changes nickname before setting topic, the broadcast prefix reflects the new nickname
# Expected: Broadcast line uses :Alicia!user@host TOPIC #chan :New Topic
CLIENTS C1, C2

# Alice and Bob join #lobby
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

# Alice changes nick to Alicia
C1 SEND NICK Alicia
C1 EXPECT :Alice!* NICK :Alicia
C2 EXPECT :Alice!* NICK :Alicia

# Alicia sets topic
C1 SEND TOPIC #lobby :Topic from Alicia
C1 EXPECT :Alicia!* TOPIC #lobby :Topic from Alicia
C2 EXPECT :Alicia!* TOPIC #lobby :Topic from Alicia
