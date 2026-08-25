# 206_QUIT_unregistered_client.spec
# Tests that an unauthenticated / unregistered client can send QUIT without triggering 451 ERR_NOTREGISTERED.
CLIENTS C1

# C1 connects and immediately sends QUIT
C1 SEND QUIT :Just looking
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT
