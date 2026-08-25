# 66_INVITE_self_invite_rejected.spec
# Tests operator attempting to INVITE themselves to a channel they already occupy.
# Expected: Server rejects with 443 ERR_USERONCHANNEL.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice66
C1 SEND USER alice66 0 * :Alice
C1 EXPECT 001 Alice66 :*
C1 SEND JOIN #selfchan66
C1 EXPECT :Alice66!* JOIN #selfchan66

# Alice attempts to invite herself
C1 SEND INVITE Alice66 #selfchan66
C1 EXPECT 443 Alice66 Alice66 #selfchan66 :is already on channel
C1 EXPECT_CONNECTED
