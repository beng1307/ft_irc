# PART removes membership, broadcasts the reason, and permits a later JOIN.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #part
C1 EXPECT :Alice!* JOIN #part
C2 SEND JOIN #part
C2 WAIT_RECV :Bob!* JOIN #part
C1 WAIT_RECV :Bob!* JOIN #part

C2 SEND PART #part :Leaving now
C1 WAIT_RECV :Bob!* PART #part :Leaving now

C2 SEND JOIN #part
C2 WAIT_RECV :Bob!* JOIN #part
C1 WAIT_RECV :Bob!* JOIN #part
C2 EXPECT_CONNECTED
