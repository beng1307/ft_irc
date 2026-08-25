# 202_QUIT_empty_colon_reason.spec
# Tests that QUIT with an empty colon argument broadcasts an empty parameter.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

C2 SEND JOIN #lobby
C2 WAIT_RECV :Bob!* JOIN #lobby
C1 WAIT_RECV :Bob!* JOIN #lobby

# Alice quits with empty colon reason
C1 SEND QUIT :
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives QUIT with empty trailing colon
C2 WAIT_RECV :Alice!* QUIT :
C2 EXPECT_CONNECTED
