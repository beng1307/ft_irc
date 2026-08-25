# 21_NICK_reconnect_rapid_nick_reclaim.spec
# Client quits, and another client immediately registers under the exact same nickname.
# Expected: Server frees the nickname immediately upon QUIT and allows reuse without ghost collision.
CLIENTS C1, C2

# C1 registers as Alice21
C1 SEND PASS 1234
C1 SEND NICK Alice21
C1 SEND USER user21 0 * :Alice 21
C1 EXPECT 001 Alice21 :*

# C1 quits
C1 SEND QUIT :Goodbye
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# C2 immediately connects and takes 'Alice21'
C2 SEND PASS 1234
C2 SEND NICK Alice21
C2 SEND USER user21 0 * :Alice 21
C2 EXPECT 001 Alice21 :*
C2 EXPECT_CONNECTED
