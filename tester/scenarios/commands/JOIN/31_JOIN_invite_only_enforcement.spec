# 31_JOIN_invite_only_enforcement.spec
# Tests standard channel invite-only (+i) mode enforcement and invite consumption upon join
# Expected:
# 1. Uninvited client receives 473 Cannot join channel (+i).
# 2. Invited client joins successfully.
# 3. Upon parting, client cannot rejoin without a fresh invite (invite is single-use).
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates #inviteonly and sets +i
C1 SEND JOIN #inviteonly
C1 SEND MODE #inviteonly +i
C1 EXPECT :Alice!* MODE #inviteonly +i

# Bob tries to join without an invite -> 473
C2 SEND JOIN #inviteonly
C2 EXPECT 473 Bob #inviteonly :Cannot join channel (+i)

# Alice invites Bob
C1 SEND INVITE Bob #inviteonly
C1 EXPECT 341 Alice Bob #inviteonly
C2 WAIT_RECV :Alice!* INVITE Bob :#inviteonly

# Bob joins successfully
C2 SEND JOIN #inviteonly
C2 EXPECT :Bob!* JOIN #inviteonly
C1 WAIT_RECV :Bob!* JOIN #inviteonly

# Bob parts the channel
C2 SEND PART #inviteonly :Leaving
C1 WAIT_RECV :Bob!* PART #inviteonly*

# Bob tries to re-join without a new invite -> 473
C2 SEND JOIN #inviteonly
C2 EXPECT 473 Bob #inviteonly :Cannot join channel (+i)
