CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #topicchan
C1 EXPECT :Alice!* JOIN #topicchan
C2 SEND JOIN #topicchan
C2 WAIT_RECV :Bob!* JOIN #topicchan
C1 WAIT_RECV :Bob!* JOIN #topicchan

C1 SEND MODE #topicchan +t
C1 WAIT_RECV :Alice!* MODE #topicchan +t

C2 SEND TOPIC #topicchan :Unauthorised Topic Change
C2 EXPECT 482 Bob #topicchan :You're not channel operator

C1 SEND TOPIC #topicchan :Official Channel Topic
C2 WAIT_RECV :Alice!* TOPIC #topicchan :Official Channel Topic
C1 WAIT_RECV :Alice!* TOPIC #topicchan :Official Channel Topic
