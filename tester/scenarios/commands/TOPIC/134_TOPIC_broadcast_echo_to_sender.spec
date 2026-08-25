# 134_TOPIC_broadcast_echo_to_sender.spec
# Tests that setting a topic broadcasts the update to the sender client as well as peers
# Expected: Sender receives :Sender!user@host TOPIC #chan :New Topic confirming topic update.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Alice sets topic and verifies self-echo broadcast
C1 SEND TOPIC #lobby :Self Echo Topic
C1 EXPECT :Alice!* TOPIC #lobby :Self Echo Topic
