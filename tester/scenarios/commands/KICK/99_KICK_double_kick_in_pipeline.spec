# 99_KICK_double_kick_in_pipeline.spec
# Tests pipelined back-to-back duplicate KICK commands on the same target.
# Expected: First KICK evicts the target; second KICK returns 441 ERR_USERNOTINCHANNEL without crashing or double-freeing.
CLIENTS C1, C2

# Alice registers and creates #lobby99K
C1 SEND PASS 1234
C1 SEND NICK Ali154
C1 SEND USER ali154 0 * :Ali154
C1 EXPECT 001 Ali154 :*
C1 SEND JOIN #lobby99K
C1 EXPECT :Ali154!* JOIN #lobby99K

# Bob registers and joins #lobby99K
C2 SEND PASS 1234
C2 SEND NICK Bob154
C2 SEND USER bob154 0 * :Bob154
C2 EXPECT 001 Bob154 :*
C2 SEND JOIN #lobby99K
C2 EXPECT :Bob154!* JOIN #lobby99K
C1 WAIT_RECV :Bob154!* JOIN #lobby99K

# Alice sends pipelined duplicate KICK commands
C1 SEND KICK #lobby99K Bob154 :First kick
C1 EXPECT :Ali154!* KICK #lobby99K Bob154 :First kick
C2 EXPECT :Ali154!* KICK #lobby99K Bob154 :First kick

# Second KICK arrives when Bob is no longer in channel
C1 SEND KICK #lobby99K Bob154 :Second kick
C1 EXPECT 441 Ali154 Bob154 #lobby99K :They aren't on that channel
