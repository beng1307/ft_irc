# 145_PART_not_on_channel_error.spec
# Tests ERR_NOTONCHANNEL (442) when parting an existing channel that the client has not joined
CLIENTS C1, C2

# Alice creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Ali214
C1 SEND USER ali214 0 * :Ali214
C1 EXPECT 001 Ali214 :*
C1 SEND JOIN #lobby
C1 EXPECT :Ali214!* JOIN #lobby

# Bob connects but does not join #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob214
C2 SEND USER bob214 0 * :Bob214
C2 EXPECT 001 Bob214 :*

# Bob tries to PART #lobby
C2 SEND PART #lobby
C2 EXPECT 442 Bob214 #lobby :You're not on that channel
