# 98_KICK_mutual_cross_kick_race.spec
# Tests race condition where two channel operators attempt to kick each other simultaneously.
# Expected: The first executed KICK evicts the second operator; the second operator's queued KICK command is rejected with 442 ERR_NOTONCHANNEL.
CLIENTS C1, C2

# Alice registers, creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers, joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice grants operator (+o) to Bob
C1 SEND MODE #lobby +o Bob
C1 EXPECT :Alice!* MODE #lobby +o Bob
C2 EXPECT :Alice!* MODE #lobby +o Bob

# Alice executes KICK against Bob
C1 SEND KICK #lobby Bob :First strike
C1 EXPECT :Alice!* KICK #lobby Bob :First strike
C2 EXPECT :Alice!* KICK #lobby Bob :First strike

# Bob's queued cross-kick attempt against Alice is processed after Bob has been evicted
C2 SEND KICK #lobby Alice :Counter strike
C2 EXPECT 442 Bob #lobby :You're not on that channel

# Alice remains in channel and can still send messages
C1 SEND PRIVMSG #lobby :I survived
C1 EXPECT_CONNECTED
