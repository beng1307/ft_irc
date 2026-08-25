# 134_TOPIC_broadcast_echo_to_sender.spec
# Tests that setting a topic broadcasts the update to the sender client as well as peers
# Expected: Sender receives :Sender!user@host TOPIC #chan :New Topic confirming topic update.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali362
C1 SEND USER ali362 0 * :Ali362
C1 EXPECT 001 Ali362 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali362!* JOIN #lobby

# Alice sets topic and verifies self-echo broadcast
C1 SEND TOPIC #lobby :Self Echo Topic
C1 EXPECT :Ali362!* TOPIC #lobby :Self Echo Topic
