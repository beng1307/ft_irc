# 51_INVITE_not_registered.spec
# Tests INVITE command issued by an unauthenticated / unregistered client.
# Expected: Server rejects with 451 ERR_NOTREGISTERED.
CLIENTS C1

# Unregistered client attempts INVITE
C1 SEND INVITE Bob #chan
C1 EXPECT 451 * :You have not registered
C1 EXPECT_CONNECTED
