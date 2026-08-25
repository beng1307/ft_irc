# 204_QUIT_colon_in_reason_emoji.spec
# Tests that QUIT with reasons starting with colon (e.g. smilies or multiple colons) preserves the colon.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali319
C1 SEND USER ali319 0 * :Ali319
C1 EXPECT 001 Ali319 :*

C2 SEND PASS 1234
C2 SEND NICK Bob319
C2 SEND USER bob319 0 * :Bob319
C2 EXPECT 001 Bob319 :*

C1 SEND JOIN #lobby231Q
C1 EXPECT :Ali319!* JOIN #lobby231Q

C2 SEND JOIN #lobby231Q
C2 WAIT_RECV :Bob319!* JOIN #lobby231Q
C1 WAIT_RECV :Bob319!* JOIN #lobby231Q

# Alice quits with smiley
C1 SEND QUIT ::)
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives exact reason
C2 WAIT_RECV :Ali319!* QUIT ::)
C2 EXPECT_CONNECTED
