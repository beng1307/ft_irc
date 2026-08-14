# TOPIC query and persistence work across PART and JOIN, while +t blocks regular users.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #topics
C1 EXPECT :Alice!* JOIN #topics
C2 SEND JOIN #topics
C2 WAIT_RECV :Bob!* JOIN #topics
C1 WAIT_RECV :Bob!* JOIN #topics

C2 SEND TOPIC #topics
C2 EXPECT 331 Bob #topics :*

C1 SEND MODE #topics +t
C1 WAIT_RECV :Alice!* MODE #topics +t
C2 SEND TOPIC #topics :blocked
C2 EXPECT 482 Bob #topics :You're not channel operator

C1 SEND TOPIC #topics :persistent topic
C2 WAIT_RECV :Alice!* TOPIC #topics :persistent topic
C1 WAIT_RECV :Alice!* TOPIC #topics :persistent topic

C2 SEND PART #topics
C2 SEND JOIN #topics
C2 WAIT_RECV :Bob!* JOIN #topics
C2 SEND TOPIC #topics
C2 EXPECT 332 Bob #topics :persistent topic
