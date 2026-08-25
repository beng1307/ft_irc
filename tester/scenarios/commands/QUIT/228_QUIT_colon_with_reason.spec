# 201_QUIT_colon_with_reason.spec
# Tests that QUIT with a multi-word trailing colon reason broadcasts the full string.
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

# Alice quits with custom multi-word reason
C1 SEND QUIT :Going out for lunch with colleagues
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives exact reason
C2 WAIT_RECV :Alice!* QUIT :Going out for lunch with colleagues
C2 EXPECT_CONNECTED
