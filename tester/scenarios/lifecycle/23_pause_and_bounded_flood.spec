# A paused client and bounded channel flood do not deadlock the server.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #flood
C1 EXPECT :Alice!* JOIN #flood
C2 SEND JOIN #flood
C2 WAIT_RECV :Bob!* JOIN #flood
C1 WAIT_RECV :Bob!* JOIN #flood
C2 PAUSE
C1 FLOOD 10 PRIVMSG #flood :bounded
C1 EXPECT_CONNECTED
C2 RESUME
C2 EXPECT_COUNT 10 PRIVMSG #flood :bounded
C2 EXPECT_CONNECTED
