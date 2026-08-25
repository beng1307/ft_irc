# 58_INVITE_unregistered_target_rejection.spec
# Tests INVITE targeting an unauthenticated / unregistered connection that only sent NICK.
# Expected: Server rejects with 401 ERR_NOSUCHNICK. Unregistered connections must not receive INVITE relays.
# Bug: Server matches nickname without checking registration status, leaks INVITE traffic to unauthenticated connection, and returns 341 RPL_INVITING.
CLIENTS C1, C2

# Alice56 registers and creates #testroom56
C1 SEND PASS 1234
C1 SEND NICK Alice56
C1 SEND USER alice56 0 * :Alice
C1 EXPECT 001 Alice56 :*
C1 SEND JOIN #testroom56
C1 EXPECT :Alice56!* JOIN #testroom56

# Bob56 connects and only sends NICK (unregistered, no PASS/USER)
C2 SEND NICK Bob56
WAIT 50ms

# Alice56 attempts to invite unregistered Bob56
C1 SEND INVITE Bob56 #testroom56
C1 EXPECT 401 Alice56 Bob56 :No such nick/channel
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
