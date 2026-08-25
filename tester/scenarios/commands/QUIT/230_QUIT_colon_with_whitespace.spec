# 203_QUIT_colon_with_whitespace.spec
# Tests that QUIT with whitespace following a colon preserves the spaces in the reason.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali318
C1 SEND USER ali318 0 * :Ali318
C1 EXPECT 001 Ali318 :*

C2 SEND PASS 1234
C2 SEND NICK Bob318
C2 SEND USER bob318 0 * :Bob318
C2 EXPECT 001 Bob318 :*

C1 SEND JOIN #lobby230Q
C1 EXPECT :Ali318!* JOIN #lobby230Q

C2 SEND JOIN #lobby230Q
C2 WAIT_RECV :Bob318!* JOIN #lobby230Q
C1 WAIT_RECV :Bob318!* JOIN #lobby230Q

# Alice quits with spaced reason
C1 SEND QUIT :   spaces preserved   
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives exact reason
C2 WAIT_RECV :Ali318!* QUIT :   spaces preserved   
C2 EXPECT_CONNECTED
