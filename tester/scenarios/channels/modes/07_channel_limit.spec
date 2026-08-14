CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #fullchan
C1 EXPECT :Alice!* JOIN #fullchan
C1 SEND MODE #fullchan +l 1
C1 WAIT_RECV :Alice!* MODE #fullchan +l 1

C2 SEND JOIN #fullchan
C2 EXPECT 471 Bob #fullchan :*

C1 SEND MODE #fullchan +l 2
C1 WAIT_RECV :Alice!* MODE #fullchan +l 2

C2 SEND JOIN #fullchan
C2 WAIT_RECV :Bob!* JOIN #fullchan
C1 WAIT_RECV :Bob!* JOIN #fullchan
