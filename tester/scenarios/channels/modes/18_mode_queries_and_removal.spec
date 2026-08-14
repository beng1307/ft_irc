# Channel mode queries expose state and each removal changes access immediately.
CLIENTS C1, C2, C3, C4

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

C4 SEND PASS 1234
C4 SEND NICK Dana
C4 SEND USER dana 0 * :Dana
C4 EXPECT 001 Dana :*

C1 SEND JOIN #modes
C1 EXPECT :Alice!* JOIN #modes
C1 SEND MODE #modes +i
C1 WAIT_RECV :Alice!* MODE #modes +i
C1 SEND MODE #modes
C1 EXPECT 324 Alice #modes +i
C1 SEND MODE #modes -i
C1 WAIT_RECV :Alice!* MODE #modes -i
C2 SEND JOIN #modes
C2 WAIT_RECV :Bob!* JOIN #modes
C1 WAIT_RECV :Bob!* JOIN #modes

C1 SEND MODE #modes +k secret
C1 WAIT_RECV :Alice!* MODE #modes +k secret
C3 SEND JOIN #modes
C3 EXPECT 475 Charlie #modes :Cannot join channel (+k)
C1 SEND MODE #modes -k
C1 WAIT_RECV :Alice!* MODE #modes -k
C3 SEND JOIN #modes
C3 WAIT_RECV :Charlie!* JOIN #modes
C1 WAIT_RECV :Charlie!* JOIN #modes

C1 SEND MODE #modes +l 3
C1 WAIT_RECV :Alice!* MODE #modes +l 3
C4 SEND JOIN #modes
C4 EXPECT 471 Dana #modes :Cannot join channel (+l)
C1 SEND MODE #modes -l
C1 WAIT_RECV :Alice!* MODE #modes -l
C4 SEND JOIN #modes
C4 WAIT_RECV :Dana!* JOIN #modes
C1 WAIT_RECV :Dana!* JOIN #modes

C1 SEND MODE #modes +t
C1 WAIT_RECV :Alice!* MODE #modes +t
C2 SEND TOPIC #modes :blocked
C2 EXPECT 482 Bob #modes :You're not channel operator
C1 SEND MODE #modes -t
C1 WAIT_RECV :Alice!* MODE #modes -t
C2 SEND TOPIC #modes :allowed
C2 WAIT_RECV :Bob!* TOPIC #modes :allowed
C1 WAIT_RECV :Bob!* TOPIC #modes :allowed

C1 SEND MODE #modes -o Alice
C1 WAIT_RECV :Alice!* MODE #modes -o Alice
C1 SEND MODE #modes +i
C1 EXPECT 482 Alice #modes :You're not channel operator
