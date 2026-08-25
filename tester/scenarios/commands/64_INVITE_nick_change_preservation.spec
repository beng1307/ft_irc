# 64_INVITE_nick_change_preservation.spec
# Tests that an invitation remains valid if the invited user changes their nickname before joining.
# Expected: User can join the +i channel under their new nickname using the existing session invitation.
CLIENTS C1, C2

# Alice64 creates invite-only channel
C1 SEND PASS 1234
C1 SEND NICK Alice64
C1 SEND USER alice64 0 * :Alice
C1 EXPECT 001 Alice64 :*
C1 SEND JOIN #priv64
C1 EXPECT :Alice64!* JOIN #priv64
C1 SEND MODE #priv64 +i
C1 EXPECT :Alice64!* MODE #priv64 +i

# Bob64 registers
C2 SEND PASS 1234
C2 SEND NICK Bob64
C2 SEND USER bob64 0 * :Bob
C2 EXPECT 001 Bob64 :*

# Alice64 invites Bob64
C1 SEND INVITE Bob64 #priv64
C1 EXPECT 341 Alice64 Bob64 #priv64
C2 WAIT_RECV :Alice64!* INVITE Bob64 :#priv64

# Bob64 changes nickname to Robert64 before joining
C2 SEND NICK Robert64
C2 WAIT_RECV :Bob64!* NICK :Robert64

# Robert64 joins #priv64
C2 SEND JOIN #priv64
C2 WAIT_RECV :Robert64!* JOIN #priv64
C1 WAIT_RECV :Robert64!* JOIN #priv64
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
