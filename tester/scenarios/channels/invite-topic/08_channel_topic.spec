CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali039
C1 SEND USER ali039 0 * :Ali039
C1 EXPECT 001 Ali039 :*

C2 SEND PASS 1234
C2 SEND NICK Bob039
C2 SEND USER bob039 0 * :Bob039
C2 EXPECT 001 Bob039 :*

C1 SEND JOIN #topicchan
C1 EXPECT :Ali039!* JOIN #topicchan
C2 SEND JOIN #topicchan
C2 WAIT_RECV :Bob039!* JOIN #topicchan
C1 WAIT_RECV :Bob039!* JOIN #topicchan

C1 SEND MODE #topicchan +t
C1 WAIT_RECV :Ali039!* MODE #topicchan +t

C2 SEND TOPIC #topicchan :Unauthorised Topic Change
C2 EXPECT 482 Bob039 #topicchan :You're not channel operator

C1 SEND TOPIC #topicchan :Official Channel Topic
C2 WAIT_RECV :Ali039!* TOPIC #topicchan :Official Channel Topic
C1 WAIT_RECV :Ali039!* TOPIC #topicchan :Official Channel Topic
