CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #testchan
C1 EXPECT :Alice!* JOIN #testchan
C2 SEND JOIN #testchan
C2 WAIT_RECV :Bob!* JOIN #testchan
C1 WAIT_RECV :Bob!* JOIN #testchan

C1 SEND PRIVMSG #testchan :Hello Channel!
C2 WAIT_RECV :Alice!* PRIVMSG #testchan :Hello Channel!
