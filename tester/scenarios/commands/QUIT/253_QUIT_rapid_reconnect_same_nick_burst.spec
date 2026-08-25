# 253_QUIT_rapid_reconnect_same_nick_burst.spec
# Tests rapid sequential disconnect and reconnection claiming the exact same nickname.
CLIENTS C1

# Cycle 1
C1 SEND PASS 1234
C1 SEND NICK RapidGhost
C1 SEND USER rapid 0 * :Rapid
C1 EXPECT 001 RapidGhost :*
C1 SEND QUIT :Cycle 1
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Cycle 2
C1 RECONNECT
C1 SEND PASS 1234
C1 SEND NICK RapidGhost
C1 SEND USER rapid 0 * :Rapid
C1 EXPECT 001 RapidGhost :*
C1 SEND QUIT :Cycle 2
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Cycle 3
C1 RECONNECT
C1 SEND PASS 1234
C1 SEND NICK RapidGhost
C1 SEND USER rapid 0 * :Rapid
C1 EXPECT 001 RapidGhost :*
C1 SEND QUIT :Cycle 3
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT
