# 76_INVITE_nick_takeover_attacker_blocked.spec
# Tests adversarial nick hijacking attempt against pending channel invitations.
# Expected: Alice invites Bob. Bob changes nickname to Bobby. An attacker (Mallory) steals the nickname 'Bob'.
# Mallory attempts to join +i channel claiming the invitation addressed to 'Bob'.
# Result: Mallory MUST be blocked with 473 ERR_INVITEONLYCHAN because invitations are tied to the client socket session, not the reclaimed nickname string.
CLIENTS C1, C2, C3

# Alice creates invite-only channel
C1 SEND PASS 1234
C1 SEND NICK Ali076
C1 SEND USER ali076 0 * :Ali101
C1 EXPECT 001 Ali076 :*
C1 SEND JOIN #vault76
C1 EXPECT :Ali076!* JOIN #vault76
C1 SEND MODE #vault76 +i
C1 EXPECT :Ali076!* MODE #vault76 +i

# Bob registers as Bob076
C2 SEND PASS 1234
C2 SEND NICK Bob101
C2 SEND USER bob101 0 * :Bob101
C2 EXPECT 001 Bob101 :*

# Alice invites Bob076
C1 SEND INVITE Bob101 #vault76
C1 EXPECT 341 Ali076 Bob101 #vault76
C2 WAIT_RECV :Ali076!* INVITE Bob101 :#vault76

# Bob changes nickname to Bby076 before joining
C2 SEND NICK Bby076
C2 WAIT_RECV :Bob101!* NICK :Bby076

# Mallory registers and immediately claims the vacated nickname 'Bob076'
C3 SEND PASS 1234
C3 SEND NICK Bob101
C3 SEND USER mal076 0 * :Mal101
C3 EXPECT 001 Bob101 :*

# Mallory tries to join #vault76 by impersonating the invited nickname
C3 SEND JOIN #vault76
# Mallory must be rejected!
C3 EXPECT 473 Bob101 #vault76 :Cannot join channel (+i)

# The legitimate recipient (Bby076) joins successfully
C2 SEND JOIN #vault76
C2 WAIT_RECV :Bby076!* JOIN #vault76
C1 WAIT_RECV :Bby076!* JOIN #vault76
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
