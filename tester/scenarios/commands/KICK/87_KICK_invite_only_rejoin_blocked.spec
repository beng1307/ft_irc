# 87_KICK_invite_only_rejoin_blocked.spec
# Tests that kicking an invited user from an invite-only (+i) channel prevents them from rejoining without a new INVITE.
CLIENTS C1, C2

# Alice registers, creates #secret, and sets +i
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #secret
C1 EXPECT :Alice!* JOIN #secret
C1 SEND MODE #secret +i
C1 EXPECT :Alice!* MODE #secret +i

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice invites Bob
C1 SEND INVITE Bob #secret
C1 EXPECT 341 Alice Bob #secret
C2 WAIT_RECV :Alice!* INVITE Bob :#secret

# Bob joins #secret
C2 SEND JOIN #secret
C2 EXPECT :Bob!* JOIN #secret
C1 WAIT_RECV :Bob!* JOIN #secret

# Alice kicks Bob
C1 SEND KICK #secret Bob :Access revoked
C1 EXPECT :Alice!* KICK #secret Bob :Access revoked
C2 EXPECT :Alice!* KICK #secret Bob :Access revoked

# Bob attempts to rejoin without a new invite
C2 SEND JOIN #secret
C2 EXPECT 473 Bob #secret :Cannot join channel (+i)
