# 74_INVITE_multi_channel_independent_invites.spec
# Tests that invitations across separate channels remain independent: consuming or parting one does not affect the other.
# Expected: Invites for #vaultA and #vaultB are tracked independently in their respective channel states.
CLIENTS C1, C2

# Alice creates two separate invite-only channels
C1 SEND PASS 1234
C1 SEND NICK Ali099
C1 SEND USER ali099 0 * :Ali099
C1 EXPECT 001 Ali099 :*
C1 SEND JOIN #vaultA74
C1 EXPECT :Ali099!* JOIN #vaultA74
C1 SEND MODE #vaultA74 +i
C1 EXPECT :Ali099!* MODE #vaultA74 +i

C1 SEND JOIN #vaultB74
C1 EXPECT :Ali099!* JOIN #vaultB74
C1 SEND MODE #vaultB74 +i
C1 EXPECT :Ali099!* MODE #vaultB74 +i

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob099
C2 SEND USER bob099 0 * :Bob099
C2 EXPECT 001 Bob099 :*

# Alice invites Bob to both channels
C1 SEND INVITE Bob099 #vaultA74
C1 EXPECT 341 Ali099 Bob099 #vaultA74
C2 WAIT_RECV :Ali099!* INVITE Bob099 :#vaultA74

C1 SEND INVITE Bob099 #vaultB74
C1 EXPECT 341 Ali099 Bob099 #vaultB74
C2 WAIT_RECV :Ali099!* INVITE Bob099 :#vaultB74

# Bob joins #vaultA74 (consuming invite for vaultA)
C2 SEND JOIN #vaultA74
C2 WAIT_RECV :Bob099!* JOIN #vaultA74

# Bob joins #vaultB74 (consuming invite for vaultB)
C2 SEND JOIN #vaultB74
C2 WAIT_RECV :Bob099!* JOIN #vaultB74

# Bob parts #vaultA74 and tries to rejoin -> Must be rejected (single-use)
C2 SEND PART #vaultA74 :leaving
C1 WAIT_RECV :Bob099!* PART #vaultA74*
C2 SEND JOIN #vaultA74
C2 EXPECT 473 Bob099 #vaultA74 :Cannot join channel (+i)

# Bob is still in #vaultB74
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
