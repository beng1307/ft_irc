# 273_TOPIC_sole_op_part_topic_lockout.spec
# Tests denial-of-service lockout where sole op enables +t, sets a topic, and parts the channel without opping anyone.
# Expected: Remaining members cannot alter or clear the topic because channel is opless and +t is active.
CLIENTS C1, C2

# Alice creates channel, enables +t, sets topic
C1 SEND PASS 1234
C1 SEND NICK Ali374
C1 SEND USER ali374 0 * :Ali374
C1 EXPECT 001 Ali374 :*
C1 SEND JOIN #locked01
C1 EXPECT :Ali374!* JOIN #locked01
C1 SEND MODE #locked01 +t
C1 EXPECT :Ali374!* MODE #locked01 +t
C1 SEND TOPIC #locked01 :Permanent Locked Topic
C1 EXPECT :Ali374!* TOPIC #locked01 :Permanent Locked Topic

# Bob joins as non-op
C2 SEND PASS 1234
C2 SEND NICK Bob374
C2 SEND USER bob374 0 * :Bob374
C2 EXPECT 001 Bob374 :*
C2 SEND JOIN #locked01
C2 EXPECT :Bob374!* JOIN #locked01
C1 WAIT_RECV :Bob374!* JOIN #locked01

# Alice parts the channel
C1 SEND PART #locked01 :Goodbye forever
C1 EXPECT :Ali374!* PART #locked01 :Goodbye forever
C2 WAIT_RECV :Ali374!* PART #locked01 :Goodbye forever

# Bob attempts to change topic in opless +t channel
C2 SEND TOPIC #locked01 :Bob374 Trying To Fix
C2 EXPECT 482 Bob374 #locked01 :You're not channel operator

# Bob attempts to clear topic
C2 SEND TOPIC #locked01 :
C2 EXPECT 482 Bob374 #locked01 :You're not channel operator

# Topic remains intact
C2 SEND TOPIC #locked01
C2 EXPECT 332 Bob374 #locked01 :Permanent Locked Topic
