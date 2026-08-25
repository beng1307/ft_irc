# 74_INVITE_multi_channel_independent_invites.spec
# Tests that invitations across separate channels remain independent: consuming or parting one does not affect the other.
# Expected: Invites for #vaultA and #vaultB are tracked independently in their respective channel states.
CLIENTS C1, C2

# Alice creates two separate invite-only channels
C1 SEND PASS 1234
C1 SEND NICK Alice74
C1 SEND USER alice74 0 * :Alice
C1 EXPECT 001 Alice74 :*
C1 SEND JOIN #vaultA74
C1 EXPECT :Alice74!* JOIN #vaultA74
C1 SEND MODE #vaultA74 +i
C1 EXPECT :Alice74!* MODE #vaultA74 +i

C1 SEND JOIN #vaultB74
C1 EXPECT :Alice74!* JOIN #vaultB74
C1 SEND MODE #vaultB74 +i
C1 EXPECT :Alice74!* MODE #vaultB74 +i

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob74
C2 SEND USER bob74 0 * :Bob
C2 EXPECT 001 Bob74 :*

# Alice invites Bob to both channels
C1 SEND INVITE Bob74 #vaultA74
C1 EXPECT 341 Alice74 Bob74 #vaultA74
C2 WAIT_RECV :Alice74!* INVITE Bob74 :#vaultA74

C1 SEND INVITE Bob74 #vaultB74
C1 EXPECT 341 Alice74 Bob74 #vaultB74
C2 WAIT_RECV :Alice74!* INVITE Bob74 :#vaultB74

# Bob joins #vaultA74 (consuming invite for vaultA)
C2 SEND JOIN #vaultA74
C2 WAIT_RECV :Bob74!* JOIN #vaultA74

# Bob joins #vaultB74 (consuming invite for vaultB)
C2 SEND JOIN #vaultB74
C2 WAIT_RECV :Bob74!* JOIN #vaultB74

# Bob parts #vaultA74 and tries to rejoin -> Must be rejected (single-use)
C2 SEND PART #vaultA74 :leaving
C1 WAIT_RECV :Bob74!* PART #vaultA74*
C2 SEND JOIN #vaultA74
C2 EXPECT 473 Bob74 #vaultA74 :Cannot join channel (+i)

# Bob is still in #vaultB74
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
