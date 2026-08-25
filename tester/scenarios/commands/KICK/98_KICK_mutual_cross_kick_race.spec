# 98_KICK_mutual_cross_kick_race.spec
# Tests race condition where two channel operators attempt to kick each other simultaneously.
# Expected: The first executed KICK evicts the second operator; the second operator's queued KICK command is rejected with 442 ERR_NOTONCHANNEL.
CLIENTS C1, C2

# Alice registers, creates #lobby98K
C1 SEND PASS 1234
C1 SEND NICK Ali153
C1 SEND USER ali153 0 * :Ali153
C1 EXPECT 001 Ali153 :*
C1 SEND JOIN #lobby98K
C1 EXPECT :Ali153!* JOIN #lobby98K

# Bob registers, joins #lobby98K
C2 SEND PASS 1234
C2 SEND NICK Bob153
C2 SEND USER bob153 0 * :Bob153
C2 EXPECT 001 Bob153 :*
C2 SEND JOIN #lobby98K
C2 EXPECT :Bob153!* JOIN #lobby98K
C1 WAIT_RECV :Bob153!* JOIN #lobby98K

# Alice grants operator (+o) to Bob
C1 SEND MODE #lobby98K +o Bob153
C1 EXPECT :Ali153!* MODE #lobby98K +o Bob153
C2 EXPECT :Ali153!* MODE #lobby98K +o Bob153

# Alice executes KICK against Bob
C1 SEND KICK #lobby98K Bob153 :First strike
C1 EXPECT :Ali153!* KICK #lobby98K Bob153 :First strike
C2 EXPECT :Ali153!* KICK #lobby98K Bob153 :First strike

# Bob's queued cross-kick attempt against Alice is processed after Bob has been evicted
C2 SEND KICK #lobby98K Ali153 :Counter strike
C2 EXPECT 442 Bob153 #lobby98K :You're not on that channel

# Alice remains in channel and can still send messages
C1 SEND PRIVMSG #lobby98K :I survived
C1 EXPECT_CONNECTED
