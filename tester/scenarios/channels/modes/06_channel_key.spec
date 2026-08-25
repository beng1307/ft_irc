CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali048
C1 SEND USER ali048 0 * :Ali048
C1 EXPECT 001 Ali048 :*

C2 SEND PASS 1234
C2 SEND NICK Bob048
C2 SEND USER bob048 0 * :Bob048
C2 EXPECT 001 Bob048 :*

C1 SEND JOIN #protected
C1 EXPECT :Ali048!* JOIN #protected
C1 SEND MODE #protected +k secret
C1 WAIT_RECV :Ali048!* MODE #protected +k secret

C2 SEND JOIN #protected
C2 EXPECT 475 Bob048 #protected :*

C2 SEND JOIN #protected secret
C2 WAIT_RECV :Bob048!* JOIN #protected
C1 WAIT_RECV :Bob048!* JOIN #protected
