# 84_KICK_self_kick_last_member_channel_destroyed.spec
# Tests self-kick when the operator is the only member in the channel.
# Expected: Server broadcasts KICK to the operator, and destroys the channel. A subsequent join by Bob creates a new channel with Bob as operator.
CLIENTS C1, C2

# Alice registers and creates #soloroom
C1 SEND PASS 1234
C1 SEND NICK Ali139
C1 SEND USER ali139 0 * :Ali139
C1 EXPECT 001 Ali139 :*
C1 SEND JOIN #soloroom
C1 EXPECT :Ali139!* JOIN #soloroom

# Alice kicks herself
C1 SEND KICK #soloroom Ali139 :leaving forever
C1 EXPECT :Ali139!* KICK #soloroom Ali139 :leaving forever

# Bob registers and joins #soloroom
C2 SEND PASS 1234
C2 SEND NICK Bob139
C2 SEND USER bob139 0 * :Bob139
C2 EXPECT 001 Bob139 :*
C2 SEND JOIN #soloroom
C2 EXPECT :Bob139!* JOIN #soloroom

# Verify Bob became channel operator in the newly created channel by setting +i
C2 SEND MODE #soloroom +i
C2 EXPECT :Bob139!* MODE #soloroom +i
