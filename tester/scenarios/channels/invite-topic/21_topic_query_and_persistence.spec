# TOPIC query and persistence work across PART and JOIN, while +t blocks regular users.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali041
C1 SEND USER ali041 0 * :Ali041
C1 EXPECT 001 Ali041 :*

C2 SEND PASS 1234
C2 SEND NICK Bob041
C2 SEND USER bob041 0 * :Bob041
C2 EXPECT 001 Bob041 :*

C1 SEND JOIN #topics
C1 EXPECT :Ali041!* JOIN #topics
C2 SEND JOIN #topics
C2 WAIT_RECV :Bob041!* JOIN #topics
C1 WAIT_RECV :Bob041!* JOIN #topics

C2 SEND TOPIC #topics
C2 EXPECT 331 Bob041 #topics :*

C1 SEND MODE #topics +t
C1 WAIT_RECV :Ali041!* MODE #topics +t
C2 SEND TOPIC #topics :blocked
C2 EXPECT 482 Bob041 #topics :You're not channel operator

C1 SEND TOPIC #topics :persistent topic
C2 WAIT_RECV :Ali041!* TOPIC #topics :persistent topic
C1 WAIT_RECV :Ali041!* TOPIC #topics :persistent topic

C2 SEND PART #topics
C2 SEND JOIN #topics
C2 WAIT_RECV :Bob041!* JOIN #topics
C2 SEND TOPIC #topics
C2 EXPECT 332 Bob041 #topics :persistent topic
