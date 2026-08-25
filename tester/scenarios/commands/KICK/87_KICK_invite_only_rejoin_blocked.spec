# 87_KICK_invite_only_rejoin_blocked.spec
# Tests that kicking an invited user from an invite-only (+i) channel prevents them from rejoining without a new INVITE.
CLIENTS C1, C2

# Alice registers, creates #secret, and sets +i
C1 SEND PASS 1234
C1 SEND NICK Ali142
C1 SEND USER ali142 0 * :Ali142
C1 EXPECT 001 Ali142 :*
C1 SEND JOIN #secret
C1 EXPECT :Ali142!* JOIN #secret
C1 SEND MODE #secret +i
C1 EXPECT :Ali142!* MODE #secret +i

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob142
C2 SEND USER bob142 0 * :Bob142
C2 EXPECT 001 Bob142 :*

# Alice invites Bob
C1 SEND INVITE Bob142 #secret
C1 EXPECT 341 Ali142 Bob142 #secret
C2 WAIT_RECV :Ali142!* INVITE Bob142 :#secret

# Bob joins #secret
C2 SEND JOIN #secret
C2 EXPECT :Bob142!* JOIN #secret
C1 WAIT_RECV :Bob142!* JOIN #secret

# Alice kicks Bob
C1 SEND KICK #secret Bob142 :Access revoked
C1 EXPECT :Ali142!* KICK #secret Bob142 :Access revoked
C2 EXPECT :Ali142!* KICK #secret Bob142 :Access revoked

# Bob attempts to rejoin without a new invite
C2 SEND JOIN #secret
C2 EXPECT 473 Bob142 #secret :Cannot join channel (+i)
