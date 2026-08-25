# 117_PART_not_on_channel_error.spec
# Tests ERR_NOTONCHANNEL (442) when parting an existing channel that the client has not joined
CLIENTS C1, C2

# Alice creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Bob connects but does not join #lobby
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Bob tries to PART #lobby
C2 SEND PART #lobby
C2 EXPECT 442 Bob #lobby :You're not on that channel
