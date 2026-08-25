# 53_MODE_demoted_operator_pipelined_retaliation.spec
# Adversarial Attack: Operator is demoted and immediately attempts to retaliate with pipelined mode changes.
# Expected: Server immediately revokes operator rights; subsequent pipelined commands from the demoted user receive 482.
CLIENTS C1, C2

# C1 is channel creator Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 is Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #room
C1 EXPECT 353 Alice = #room :@Alice
C1 EXPECT 366 Alice #room :End of /NAMES list

C2 SEND JOIN #room
C1 WAIT_RECV :Bob!* JOIN #room

# Alice promotes Bob to operator
C1 SEND MODE #room +o Bob
C1 EXPECT :Alice!* MODE #room +o Bob
C2 EXPECT :Alice!* MODE #room +o Bob

# Alice demotes Bob back to regular member
C1 SEND MODE #room -o Bob
C1 EXPECT :Alice!* MODE #room -o Bob
C2 EXPECT :Alice!* MODE #room -o Bob

# Bob immediately attempts retaliation (de-opping Alice or setting +i)
C2 SEND MODE #room -o Alice
C2 EXPECT 482 Bob #room :You're not channel operator

C2 SEND MODE #room +i
C2 EXPECT 482 Bob #room :You're not channel operator

# Verify Alice is still operator
C1 SEND KICK #room Bob :Demoted and kicked
C1 EXPECT :Alice!* KICK #room Bob :Demoted and kicked
