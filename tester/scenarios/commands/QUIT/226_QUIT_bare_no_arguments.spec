# 199_QUIT_bare_no_arguments.spec
# Tests that bare QUIT without arguments broadcasts default reason "Leaving server" to mutual channels and closes socket.
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

# Alice sends bare QUIT
C1 SEND QUIT
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives default reason broadcast
C2 WAIT_RECV :Alice!* QUIT :Leaving server
C2 EXPECT_CONNECTED
