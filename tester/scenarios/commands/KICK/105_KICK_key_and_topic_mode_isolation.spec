# 105_KICK_key_and_topic_mode_isolation.spec
# Tests that kicking a user from a channel with topic (+t) and key (+k) preserves channel security parameters and does not leak keys or reset topic.
CLIENTS C1, C2

# Alice registers, creates #secure, sets +t, topic, and +k
C1 SEND PASS 1234
C1 SEND NICK Ali126
C1 SEND USER ali126 0 * :Ali126
C1 EXPECT 001 Ali126 :*
C1 SEND JOIN #secure
C1 EXPECT :Ali126!* JOIN #secure
C1 SEND TOPIC #secure :Classified Topic
C1 EXPECT :Ali126!* TOPIC #secure :Classified Topic
C1 SEND MODE #secure +t
C1 EXPECT :Ali126!* MODE #secure +t
C1 SEND MODE #secure +k Secret123
C1 EXPECT :Ali126!* MODE #secure +k Secret123

# Bob registers and joins with key
C2 SEND PASS 1234
C2 SEND NICK Bob126
C2 SEND USER bob126 0 * :Bob126
C2 EXPECT 001 Bob126 :*
C2 SEND JOIN #secure Secret123
C2 EXPECT :Bob126!* JOIN #secure
C1 WAIT_RECV :Bob126!* JOIN #secure

# Alice kicks Bob
C1 SEND KICK #secure Bob126 :Access terminated
C1 EXPECT :Ali126!* KICK #secure Bob126 :Access terminated
C2 EXPECT :Ali126!* KICK #secure Bob126 :Access terminated

# Bob tries to set topic while not in channel
C2 SEND TOPIC #secure :Hacked Topic
C2 EXPECT 442 Bob126 #secure :You're not on that channel

# Bob tries to rejoin without key -> rejected with 475
C2 SEND JOIN #secure
C2 EXPECT 475 Bob126 #secure :Cannot join channel (+k)

# Alice verifies topic is intact
C1 SEND TOPIC #secure
C1 EXPECT 332 Ali126 #secure :Classified Topic
