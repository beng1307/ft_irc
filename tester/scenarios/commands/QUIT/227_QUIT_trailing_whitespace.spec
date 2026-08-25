# 200_QUIT_trailing_whitespace.spec
# Tests that QUIT followed by trailing whitespace trims arguments and defaults to "Leaving server".
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali315
C1 SEND USER ali315 0 * :Ali315
C1 EXPECT 001 Ali315 :*

C2 SEND PASS 1234
C2 SEND NICK Bob315
C2 SEND USER bob315 0 * :Bob315
C2 EXPECT 001 Bob315 :*

C1 SEND JOIN #lobby227Q
C1 EXPECT :Ali315!* JOIN #lobby227Q

C2 SEND JOIN #lobby227Q
C2 WAIT_RECV :Bob315!* JOIN #lobby227Q
C1 WAIT_RECV :Bob315!* JOIN #lobby227Q

# Alice sends QUIT with trailing spaces
C1 SEND QUIT    
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives default reason broadcast
C2 WAIT_RECV :Ali315!* QUIT :Leaving server
C2 EXPECT_CONNECTED
