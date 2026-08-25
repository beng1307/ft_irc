# 260_PASS_unauthenticated_nick_eviction.spec
# Adversarial Scenario: Unauthenticated client C1 holds nickname in pre-auth limbo.
# Authenticated client C2 provides valid PASS and takes the nickname. Server must allow C2 to register.
CLIENTS C1, C2

# C1 attempts to squat on nickname without password
C1 SEND NICK Vic259
C1 SEND USER unauth 0 * :Unauthenticated

# C2 authenticates with correct password and claims nickname
C2 SEND PASS 1234
C2 SEND NICK Vic259
C2 SEND USER vic259 0 * :Legit Usr259
C2 EXPECT 001 Vic259 :*
