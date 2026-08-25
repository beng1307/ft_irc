# 78_KICK_target_not_on_channel.spec
# Tests that an operator attempting to KICK a registered user who is NOT in the channel returns ERR_USERNOTINCHANNEL (441).
CLIENTS C1, C2

# Alice registers and creates #lobby78K
C1 SEND PASS 1234
C1 SEND NICK Ali133
C1 SEND USER ali133 0 * :Ali133
C1 EXPECT 001 Ali133 :*
C1 SEND JOIN #lobby78K
C1 EXPECT :Ali133!* JOIN #lobby78K

# Bob registers but does not join #lobby78K
C2 SEND PASS 1234
C2 SEND NICK Bob133
C2 SEND USER bob133 0 * :Bob133
C2 EXPECT 001 Bob133 :*

# Alice attempts to kick Bob from #lobby78K
C1 SEND KICK #lobby78K Bob133 :not here
C1 EXPECT 441 Ali133 Bob133 #lobby78K :They aren't on that channel
