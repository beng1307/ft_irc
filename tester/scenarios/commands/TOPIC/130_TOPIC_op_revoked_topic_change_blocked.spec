# 130_TOPIC_op_revoked_topic_change_blocked.spec
# Tests revoking operator privileges (MODE -o) dynamically blocks topic changes in +t channel
# Expected: Once -o is applied, user is blocked with 482 ERR_CHANOPRIVSNEEDED.
CLIENTS C1, C2

# Alice creates channel, enables +t, and ops Bob
C1 SEND PASS 1234
C1 SEND NICK Ali358
C1 SEND USER ali358 0 * :Ali358
C1 EXPECT 001 Ali358 :*
C1 SEND JOIN #gated
C1 EXPECT :Ali358!* JOIN #gated
C1 SEND MODE #gated +t
C1 EXPECT :Ali358!* MODE #gated +t

C2 SEND PASS 1234
C2 SEND NICK Bob358
C2 SEND USER bob358 0 * :Bob358
C2 EXPECT 001 Bob358 :*
C2 SEND JOIN #gated
C2 EXPECT :Bob358!* JOIN #gated
C1 WAIT_RECV :Bob358!* JOIN #gated

C1 SEND MODE #gated +o Bob358
C1 EXPECT :Ali358!* MODE #gated +o Bob358
C2 EXPECT :Ali358!* MODE #gated +o Bob358

# Alice de-ops Bob
C1 SEND MODE #gated -o Bob358
C1 EXPECT :Ali358!* MODE #gated -o Bob358
C2 EXPECT :Ali358!* MODE #gated -o Bob358

# Bob tries to set topic and gets blocked
C2 SEND TOPIC #gated :Unauthorized after de-op
C2 EXPECT 482 Bob358 #gated :You're not channel operator
