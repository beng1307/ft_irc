# 31_JOIN_invite_only_enforcement.spec
# Tests standard channel invite-only (+i) mode enforcement and invite consumption upon join
# Expected:
# 1. Uninvited client receives 473 Cannot join channel (+i).
# 2. Invited client joins successfully.
# 3. Upon parting, client cannot rejoin without a fresh invite (invite is single-use).
CLIENTS C1, C2

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Ali114
C1 SEND USER ali114 0 * :Ali114
C1 EXPECT 001 Ali114 :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob114
C2 SEND USER bob114 0 * :Bob114
C2 EXPECT 001 Bob114 :*

# Alice creates #inviteonly and sets +i
C1 SEND JOIN #inviteonly
C1 SEND MODE #inviteonly +i
C1 EXPECT :Ali114!* MODE #inviteonly +i

# Bob tries to join without an invite -> 473
C2 SEND JOIN #inviteonly
C2 EXPECT 473 Bob114 #inviteonly :Cannot join channel (+i)

# Alice invites Bob
C1 SEND INVITE Bob114 #inviteonly
C1 EXPECT 341 Ali114 Bob114 #inviteonly
C2 WAIT_RECV :Ali114!* INVITE Bob114 :#inviteonly

# Bob joins successfully
C2 SEND JOIN #inviteonly
C2 EXPECT :Bob114!* JOIN #inviteonly
C1 WAIT_RECV :Bob114!* JOIN #inviteonly

# Bob parts the channel
C2 SEND PART #inviteonly :Leaving
C1 WAIT_RECV :Bob114!* PART #inviteonly*

# Bob tries to re-join without a new invite -> 473
C2 SEND JOIN #inviteonly
C2 EXPECT 473 Bob114 #inviteonly :Cannot join channel (+i)
