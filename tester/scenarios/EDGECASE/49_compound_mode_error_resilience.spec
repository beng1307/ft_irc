# Scenario 49: Compound Mode Error Resilience and Normalization
# Tests compound mode strings containing unknown characters, missing parameters,
# non-member targets, and redundant polarity signs to ensure proper error emission,
# omitted invalid flags, and broadcast of only the valid, applied modes.
CLIENTS C1, C2, C3

# Register Alice, Bob, and Charlie
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# Alice creates #moderesilience and sets initial limit (+l 10)
C1 SEND JOIN #moderesilience
C1 EXPECT :Alice!* JOIN #moderesilience
C1 SEND MODE #moderesilience +l 10
C1 EXPECT :Alice!* MODE #moderesilience +l 10

# Bob joins
C2 SEND JOIN #moderesilience
C2 WAIT_RECV :Bob!* JOIN #moderesilience
C1 WAIT_RECV :Bob!* JOIN #moderesilience

# Case 1: Interleaved unknown mode character ('5') with valid modes (+i, +t, -l, +o Bob)
# Alice should receive 472 for '5', and the broadcast should contain only valid modes (+it-l+o Bob)
C1 SEND MODE #moderesilience +i5t-l+o Bob
C1 EXPECT 472 Alice 5 :is unknown mode char to me
C1 EXPECT :Alice!* MODE #moderesilience +it-l+o Bob
C2 WAIT_RECV :Alice!* MODE #moderesilience +it-l+o Bob

# Case 2: +o targeting a user who is registered but not in the channel (Charlie)
# Alice should receive 441, +o Charlie is omitted, and only valid modes (+k secretkey) are broadcasted
C1 SEND MODE #moderesilience +ko secretkey Charlie
C1 EXPECT 441 Alice Charlie #moderesilience :They aren't on that channel
C1 EXPECT :Alice!* MODE #moderesilience +k secretkey
C2 WAIT_RECV :Alice!* MODE #moderesilience +k secretkey

# Case 3: +o targeting a completely non-existent nickname (GhostUser)
# Alice should receive 401, +o GhostUser is omitted
C1 SEND MODE #moderesilience +o GhostUser
C1 EXPECT 401 Alice GhostUser :No such nick/channel

# Case 4: Redundant polarity symbols (++i--t)
# Should normalize properly to -t (+i is already set, so -t is applied)
C1 SEND MODE #moderesilience ++i--t
C1 EXPECT :Alice!* MODE #moderesilience +i-t
C2 WAIT_RECV :Alice!* MODE #moderesilience +i-t

# Case 5: Invalid parameter for limit (+l invalid_limit)
# Should emit 461 and not apply the limit change
C1 SEND MODE #moderesilience +l abc
C1 EXPECT 461 Alice MODE :Not enough parameters

# Verify final active channel modes via MODE query
C1 SEND MODE #moderesilience
C1 EXPECT 324 Alice #moderesilience +ik secretkey
