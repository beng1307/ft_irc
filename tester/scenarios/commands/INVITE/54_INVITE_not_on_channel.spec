# 54_INVITE_not_on_channel.spec
# Tests INVITE issued by a user who is not a member of the target channel.
# Expected: Server rejects with 442 ERR_NOTONCHANNEL.
CLIENTS C1, C2

# C1 registers as Alice52
C1 SEND PASS 1234
C1 SEND NICK Alice52
C1 SEND USER alice52 0 * :Alice
C1 EXPECT 001 Alice52 :*

# C2 registers as Bob52 and creates #bobsroom52
C2 SEND PASS 1234
C2 SEND NICK Bob52
C2 SEND USER bob52 0 * :Bob
C2 EXPECT 001 Bob52 :*
C2 SEND JOIN #bobsroom52
C2 EXPECT :Bob52!* JOIN #bobsroom52

# Alice52 (not in #bobsroom52) tries to invite Charlie to #bobsroom52
C1 SEND INVITE Charlie #bobsroom52
C1 EXPECT 442 Alice52 #bobsroom52 :You're not on that channel
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
