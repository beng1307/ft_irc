# Tests ghost channel re-creation hijack prevention (ADV-STATE-07), invite case insensitivity (ADV-STATE-05), and operator boundary integrity.
CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# ADV-STATE-07: Ghost channel re-creation hijack test
# Alice creates #GhostChan (Alice is op)
C1 SEND JOIN #GhostChan
C1 EXPECT :Alice!* JOIN #GhostChan

# Bob joins #GhostChan (Bob is regular user)
C2 SEND JOIN #GhostChan
C2 WAIT_RECV :Bob!* JOIN #GhostChan
C1 WAIT_RECV :Bob!* JOIN #GhostChan

# Alice parts #GhostChan -> now only Bob is in #GhostChan (no ops)
C1 SEND PART #GhostChan :bye
C2 WAIT_RECV :Alice!* PART #GhostChan*

# Alice rejoins #GhostChan -> Alice must NOT get op back because channel was not empty
C1 SEND JOIN #GhostChan
C1 EXPECT :Alice!* JOIN #GhostChan
C2 WAIT_RECV :Alice!* JOIN #GhostChan

# Alice tries to kick Bob -> fails with 482 because Alice is a regular user
C1 SEND KICK #GhostChan Bob :illegal kick
C1 EXPECT 482 Alice #GhostChan :*

# ADV-STATE-05: Invite and case insensitivity collision
# Charlie creates #InviteCase and sets +i
C3 SEND JOIN #InviteCase
C3 EXPECT :Charlie!* JOIN #InviteCase
C3 SEND MODE #InviteCase +i
C3 WAIT_RECV :Charlie!* MODE #InviteCase +i

# Charlie invites Alice using all-lowercase channel name
C3 SEND INVITE Alice #invitecase
C3 EXPECT 341 Charlie Alice #invitecase
C1 WAIT_RECV :Charlie!* INVITE Alice :#invitecase

# Alice joins using all-uppercase channel name
C1 SEND JOIN #INVITECASE
C1 WAIT_RECV :Alice!* JOIN #*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
