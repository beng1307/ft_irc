# 273_TOPIC_sole_op_part_topic_lockout.spec
# Tests denial-of-service lockout where sole op enables +t, sets a topic, and parts the channel without opping anyone.
# Expected: Remaining members cannot alter or clear the topic because channel is opless and +t is active.
CLIENTS C1, C2

# Alice creates channel, enables +t, sets topic
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #locked
C1 EXPECT :Alice!* JOIN #locked
C1 SEND MODE #locked +t
C1 EXPECT :Alice!* MODE #locked +t
C1 SEND TOPIC #locked :Permanent Locked Topic
C1 EXPECT :Alice!* TOPIC #locked :Permanent Locked Topic

# Bob joins as non-op
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #locked
C2 EXPECT :Bob!* JOIN #locked
C1 WAIT_RECV :Bob!* JOIN #locked

# Alice parts the channel
C1 SEND PART #locked :Goodbye forever
C1 EXPECT :Alice!* PART #locked :Goodbye forever
C2 WAIT_RECV :Alice!* PART #locked :Goodbye forever

# Bob attempts to change topic in opless +t channel
C2 SEND TOPIC #locked :Bob Trying To Fix
C2 EXPECT 482 Bob #locked :You're not channel operator

# Bob attempts to clear topic
C2 SEND TOPIC #locked :
C2 EXPECT 482 Bob #locked :You're not channel operator

# Topic remains intact
C2 SEND TOPIC #locked
C2 EXPECT 332 Bob #locked :Permanent Locked Topic
