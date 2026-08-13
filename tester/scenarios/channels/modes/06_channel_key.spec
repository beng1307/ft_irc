CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob

C1 SEND JOIN #protected
C1 SEND MODE #protected +k secret

C2 SEND JOIN #protected
C2 EXPECT 475 Bob #protected :*

C2 SEND JOIN #protected secret
C1 WAIT_RECV :Bob!* JOIN #protected
