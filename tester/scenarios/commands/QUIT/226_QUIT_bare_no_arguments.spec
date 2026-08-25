# 199_QUIT_bare_no_arguments.spec
# Tests that bare QUIT without arguments broadcasts default reason "Leaving server" to mutual channels and closes socket.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali314
C1 SEND USER ali314 0 * :Ali314
C1 EXPECT 001 Ali314 :*

C2 SEND PASS 1234
C2 SEND NICK Bob314
C2 SEND USER bob314 0 * :Bob314
C2 EXPECT 001 Bob314 :*

C1 SEND JOIN #lobby226Q
C1 EXPECT :Ali314!* JOIN #lobby226Q

C2 SEND JOIN #lobby226Q
C2 WAIT_RECV :Bob314!* JOIN #lobby226Q
C1 WAIT_RECV :Bob314!* JOIN #lobby226Q

# Alice sends bare QUIT
C1 SEND QUIT
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives default reason broadcast
C2 WAIT_RECV :Ali314!* QUIT :Leaving server
C2 EXPECT_CONNECTED
