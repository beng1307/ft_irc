# 68_INVITE_self_invite_rejected.spec
# Tests operator attempting to INVITE themselves to a channel they already occupy.
# Expected: Server rejects with 443 ERR_USERONCHANNEL.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali093
C1 SEND USER ali093 0 * :Ali093
C1 EXPECT 001 Ali093 :*
C1 SEND JOIN #selfchan66
C1 EXPECT :Ali093!* JOIN #selfchan66

# Alice attempts to invite herself
C1 SEND INVITE Ali093 #selfchan66
C1 EXPECT 443 Ali093 Ali093 #selfchan66 :is already on channel
C1 EXPECT_CONNECTED
