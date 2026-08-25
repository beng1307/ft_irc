# 137_TOPIC_nick_change_broadcaster_prefix.spec
# Tests that when a user changes nickname before setting topic, the broadcast prefix reflects the new nickname
# Expected: Broadcast line uses :Alicia!user@host TOPIC #chan :New Topic
CLIENTS C1, C2

# Alice and Bob join #lobby137T
C1 SEND PASS 1234
C1 SEND NICK Ali365
C1 SEND USER ali365 0 * :Ali365
C1 EXPECT 001 Ali365 :*
C1 SEND JOIN #lobby137T
C1 EXPECT :Ali365!* JOIN #lobby137T

C2 SEND PASS 1234
C2 SEND NICK Bob365
C2 SEND USER bob365 0 * :Bob365
C2 EXPECT 001 Bob365 :*
C2 SEND JOIN #lobby137T
C2 EXPECT :Bob365!* JOIN #lobby137T
C1 WAIT_RECV :Bob365!* JOIN #lobby137T

# Alice changes nick to Alicia
C1 SEND NICK Ali365
C1 EXPECT :Ali365!* NICK :Ali365
C2 EXPECT :Ali365!* NICK :Ali365

# Alicia sets topic
C1 SEND TOPIC #lobby137T :Topic from Ali365
C1 EXPECT :Ali365!* TOPIC #lobby137T :Topic from Ali365
C2 EXPECT :Ali365!* TOPIC #lobby137T :Topic from Ali365
