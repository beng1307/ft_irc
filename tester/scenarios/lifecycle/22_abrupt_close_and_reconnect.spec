# Abrupt client termination does not stop the server, and a new client can reuse the nick.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #lifecycle
C1 EXPECT :Alice!* JOIN #lifecycle
C2 SEND JOIN #lifecycle
C2 WAIT_RECV :Bob!* JOIN #lifecycle
C1 WAIT_RECV :Bob!* JOIN #lifecycle
C2 RESET
C2 EXPECT_DISCONNECT
C1 EXPECT_CONNECTED
C1 SEND PRIVMSG Alice :server remains alive
C2 RECONNECT
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 EXPECT_CONNECTED
