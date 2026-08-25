# 102_TOPIC_op_revoked_topic_change_blocked.spec
# Tests revoking operator privileges (MODE -o) dynamically blocks topic changes in +t channel
# Expected: Once -o is applied, user is blocked with 482 ERR_CHANOPRIVSNEEDED.
CLIENTS C1, C2

# Alice creates channel, enables +t, and ops Bob
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #gated
C1 EXPECT :Alice!* JOIN #gated
C1 SEND MODE #gated +t
C1 EXPECT :Alice!* MODE #gated +t

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #gated
C2 EXPECT :Bob!* JOIN #gated
C1 WAIT_RECV :Bob!* JOIN #gated

C1 SEND MODE #gated +o Bob
C1 EXPECT :Alice!* MODE #gated +o Bob
C2 EXPECT :Alice!* MODE #gated +o Bob

# Alice de-ops Bob
C1 SEND MODE #gated -o Bob
C1 EXPECT :Alice!* MODE #gated -o Bob
C2 EXPECT :Alice!* MODE #gated -o Bob

# Bob tries to set topic and gets blocked
C2 SEND TOPIC #gated :Unauthorized after de-op
C2 EXPECT 482 Bob #gated :You're not channel operator
