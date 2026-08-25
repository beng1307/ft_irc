# 99_KICK_double_kick_in_pipeline.spec
# Tests pipelined back-to-back duplicate KICK commands on the same target.
# Expected: First KICK evicts the target; second KICK returns 441 ERR_USERNOTINCHANNEL without crashing or double-freeing.
CLIENTS C1, C2

# Alice registers and creates #lobby
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

# Alice sends pipelined duplicate KICK commands
C1 SEND KICK #lobby Bob :First kick
C1 EXPECT :Alice!* KICK #lobby Bob :First kick
C2 EXPECT :Alice!* KICK #lobby Bob :First kick

# Second KICK arrives when Bob is no longer in channel
C1 SEND KICK #lobby Bob :Second kick
C1 EXPECT 441 Alice Bob #lobby :They aren't on that channel
