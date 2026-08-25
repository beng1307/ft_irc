# 105_KICK_key_and_topic_mode_isolation.spec
# Tests that kicking a user from a channel with topic (+t) and key (+k) preserves channel security parameters and does not leak keys or reset topic.
CLIENTS C1, C2

# Alice registers, creates #secure, sets +t, topic, and +k
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #secure
C1 EXPECT :Alice!* JOIN #secure
C1 SEND TOPIC #secure :Classified Topic
C1 EXPECT :Alice!* TOPIC #secure :Classified Topic
C1 SEND MODE #secure +t
C1 EXPECT :Alice!* MODE #secure +t
C1 SEND MODE #secure +k Secret123
C1 EXPECT :Alice!* MODE #secure +k Secret123

# Bob registers and joins with key
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #secure Secret123
C2 EXPECT :Bob!* JOIN #secure
C1 WAIT_RECV :Bob!* JOIN #secure

# Alice kicks Bob
C1 SEND KICK #secure Bob :Access terminated
C1 EXPECT :Alice!* KICK #secure Bob :Access terminated
C2 EXPECT :Alice!* KICK #secure Bob :Access terminated

# Bob tries to set topic while not in channel
C2 SEND TOPIC #secure :Hacked Topic
C2 EXPECT 442 Bob #secure :You're not on that channel

# Bob tries to rejoin without key -> rejected with 475
C2 SEND JOIN #secure
C2 EXPECT 475 Bob #secure :Cannot join channel (+k)

# Alice verifies topic is intact
C1 SEND TOPIC #secure
C1 EXPECT 332 Alice #secure :Classified Topic
