# 55_INVITE_target_already_on_channel.spec
# Tests INVITE issued targeting a user who is already in the channel.
# Expected: Server rejects with 443 ERR_USERONCHANNEL.
CLIENTS C1, C2

# Alice55 creates #testroom55
C1 SEND PASS 1234
C1 SEND NICK Alice55
C1 SEND USER alice55 0 * :Alice
C1 EXPECT 001 Alice55 :*
C1 SEND JOIN #testroom55
C1 EXPECT :Alice55!* JOIN #testroom55

# Bob55 registers and joins #testroom55
C2 SEND PASS 1234
C2 SEND NICK Bob55
C2 SEND USER bob55 0 * :Bob
C2 EXPECT 001 Bob55 :*
C2 SEND JOIN #testroom55
C2 EXPECT :Bob55!* JOIN #testroom55

# Alice55 attempts to invite Bob55 who is already in #testroom55
C1 SEND INVITE Bob55 #testroom55
C1 EXPECT 443 Alice55 Bob55 #testroom55 :is already on channel
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
