# 53_MODE_demoted_operator_pipelined_retaliation.spec
# Adversarial Attack: Operator is demoted and immediately attempts to retaliate with pipelined mode changes.
# Expected: Server immediately revokes operator rights; subsequent pipelined commands from the demoted user receive 482.
CLIENTS C1, C2

# C1 is channel creator Alice
C1 SEND PASS 1234
C1 SEND NICK Ali170
C1 SEND USER ali170 0 * :Ali170
C1 EXPECT 001 Ali170 :*

# C2 is Bob
C2 SEND PASS 1234
C2 SEND NICK Bob170
C2 SEND USER bob170 0 * :Bob170
C2 EXPECT 001 Bob170 :*

C1 SEND JOIN #room01
C1 EXPECT 353 Ali170 = #room01 :@Ali170
C1 EXPECT 366 Ali170 #room01 :End of /NAMES list

C2 SEND JOIN #room01
C1 WAIT_RECV :Bob170!* JOIN #room01

# Alice promotes Bob to operator
C1 SEND MODE #room01 +o Bob170
C1 EXPECT :Ali170!* MODE #room01 +o Bob170
C2 EXPECT :Ali170!* MODE #room01 +o Bob170

# Alice demotes Bob back to regular member
C1 SEND MODE #room01 -o Bob170
C1 EXPECT :Ali170!* MODE #room01 -o Bob170
C2 EXPECT :Ali170!* MODE #room01 -o Bob170

# Bob immediately attempts retaliation (de-opping Alice or setting +i)
C2 SEND MODE #room01 -o Ali170
C2 EXPECT 482 Bob170 #room01 :You're not channel operator

C2 SEND MODE #room01 +i
C2 EXPECT 482 Bob170 #room01 :You're not channel operator

# Verify Alice is still operator
C1 SEND KICK #room01 Bob170 :Demoted and kicked
C1 EXPECT :Ali170!* KICK #room01 Bob170 :Demoted and kicked
