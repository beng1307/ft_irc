# Channel mode queries expose state and each removal changes access immediately.
CLIENTS C1, C2, C3, C4

C1 SEND PASS 1234
C1 SEND NICK Ali018
C1 SEND USER ali018 0 * :Ali018
C1 EXPECT 001 Ali018 :*

C2 SEND PASS 1234
C2 SEND NICK Bob051
C2 SEND USER bob051 0 * :Bob051
C2 EXPECT 001 Bob051 :*

C3 SEND PASS 1234
C3 SEND NICK Cha018
C3 SEND USER cha018 0 * :Cha018
C3 EXPECT 001 Cha018 :*

C4 SEND PASS 1234
C4 SEND NICK Dan018
C4 SEND USER dan018 0 * :Dan018
C4 EXPECT 001 Dan018 :*

C1 SEND JOIN #modes
C1 EXPECT :Ali018!* JOIN #modes
C1 SEND MODE #modes +i
C1 WAIT_RECV :Ali018!* MODE #modes +i
C1 SEND MODE #modes
C1 EXPECT 324 Ali018 #modes +i
C1 SEND MODE #modes -i
C1 WAIT_RECV :Ali018!* MODE #modes -i
C2 SEND JOIN #modes
C2 WAIT_RECV :Bob051!* JOIN #modes
C1 WAIT_RECV :Bob051!* JOIN #modes

C1 SEND MODE #modes +k secret
C1 WAIT_RECV :Ali018!* MODE #modes +k secret
C3 SEND JOIN #modes
C3 EXPECT 475 Cha018 #modes :Cannot join channel (+k)
C1 SEND MODE #modes -k
C1 WAIT_RECV :Ali018!* MODE #modes -k
C3 SEND JOIN #modes
C3 WAIT_RECV :Cha018!* JOIN #modes
C1 WAIT_RECV :Cha018!* JOIN #modes

C1 SEND MODE #modes +l 3
C1 WAIT_RECV :Ali018!* MODE #modes +l 3
C4 SEND JOIN #modes
C4 EXPECT 471 Dan018 #modes :Cannot join channel (+l)
C1 SEND MODE #modes -l
C1 WAIT_RECV :Ali018!* MODE #modes -l
C4 SEND JOIN #modes
C4 WAIT_RECV :Dan018!* JOIN #modes
C1 WAIT_RECV :Dan018!* JOIN #modes

C1 SEND MODE #modes +t
C1 WAIT_RECV :Ali018!* MODE #modes +t
C2 SEND TOPIC #modes :blocked
C2 EXPECT 482 Bob051 #modes :You're not channel operator
C1 SEND MODE #modes -t
C1 WAIT_RECV :Ali018!* MODE #modes -t
C2 SEND TOPIC #modes :allowed
C2 WAIT_RECV :Bob051!* TOPIC #modes :allowed
C1 WAIT_RECV :Bob051!* TOPIC #modes :allowed

C1 SEND MODE #modes -o Ali018
C1 WAIT_RECV :Ali018!* MODE #modes -o Ali018
C1 SEND MODE #modes +i
C1 EXPECT 482 Ali018 #modes :You're not channel operator
