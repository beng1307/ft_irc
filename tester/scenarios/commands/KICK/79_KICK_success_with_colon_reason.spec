# 79_KICK_success_with_colon_reason.spec
# Tests successful KICK with standard colon-prefixed reason.
# Expected: Server broadcasts KICK message to all channel members (including kicked user), and removes target from channel.
CLIENTS C1, C2, C3

# Alice registers and creates #lobby (op)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob registers and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #lobby
C2 EXPECT :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Charlie registers and joins #lobby
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*
C3 SEND JOIN #lobby
C3 EXPECT :Charlie!* JOIN #lobby
C1 WAIT_RECV :Charlie!* JOIN #lobby
C2 WAIT_RECV :Charlie!* JOIN #lobby

# Alice kicks Bob with colon reason
C1 SEND KICK #lobby Bob :Bad behavior in channel
C1 EXPECT :Alice!* KICK #lobby Bob :Bad behavior in channel
C2 EXPECT :Alice!* KICK #lobby Bob :Bad behavior in channel
C3 EXPECT :Alice!* KICK #lobby Bob :Bad behavior in channel

# Bob is now no longer on channel, cannot PRIVMSG #lobby
C2 SEND PRIVMSG #lobby :Am I still here?
C2 EXPECT 404 Bob #lobby :Cannot send to channel

