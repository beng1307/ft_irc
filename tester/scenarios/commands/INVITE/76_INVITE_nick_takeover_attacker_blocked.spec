# 76_INVITE_nick_takeover_attacker_blocked.spec
# Tests adversarial nick hijacking attempt against pending channel invitations.
# Expected: Alice invites Bob. Bob changes nickname to Bobby. An attacker (Mallory) steals the nickname 'Bob'.
# Mallory attempts to join +i channel claiming the invitation addressed to 'Bob'.
# Result: Mallory MUST be blocked with 473 ERR_INVITEONLYCHAN because invitations are tied to the client socket session, not the reclaimed nickname string.
CLIENTS C1, C2, C3

# Alice creates invite-only channel
C1 SEND PASS 1234
C1 SEND NICK Alice76
C1 SEND USER alice76 0 * :Alice
C1 EXPECT 001 Alice76 :*
C1 SEND JOIN #vault76
C1 EXPECT :Alice76!* JOIN #vault76
C1 SEND MODE #vault76 +i
C1 EXPECT :Alice76!* MODE #vault76 +i

# Bob registers as Bob76
C2 SEND PASS 1234
C2 SEND NICK Bob76
C2 SEND USER bob76 0 * :Bob
C2 EXPECT 001 Bob76 :*

# Alice invites Bob76
C1 SEND INVITE Bob76 #vault76
C1 EXPECT 341 Alice76 Bob76 #vault76
C2 WAIT_RECV :Alice76!* INVITE Bob76 :#vault76

# Bob changes nickname to Bobby76 before joining
C2 SEND NICK Bobby76
C2 WAIT_RECV :Bob76!* NICK :Bobby76

# Mallory registers and immediately claims the vacated nickname 'Bob76'
C3 SEND PASS 1234
C3 SEND NICK Bob76
C3 SEND USER mallory76 0 * :Mallory
C3 EXPECT 001 Bob76 :*

# Mallory tries to join #vault76 by impersonating the invited nickname
C3 SEND JOIN #vault76
# Mallory must be rejected!
C3 EXPECT 473 Bob76 #vault76 :Cannot join channel (+i)

# The legitimate recipient (Bobby76) joins successfully
C2 SEND JOIN #vault76
C2 WAIT_RECV :Bobby76!* JOIN #vault76
C1 WAIT_RECV :Bobby76!* JOIN #vault76
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
