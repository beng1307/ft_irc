# 218_QUIT_case_insensitivity.spec
# Tests that lowercase and mixed-case QUIT commands (quit, QuiT) are properly dispatched.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #mixed
C1 EXPECT :Alice!* JOIN #mixed
C2 SEND JOIN #mixed
C2 WAIT_RECV :Bob!* JOIN #mixed
C1 WAIT_RECV :Bob!* JOIN #mixed

# Bob sends lowercase 'quit'
C2 SEND quit :Lowercase quit
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECT
C1 WAIT_RECV :Bob!* QUIT :Lowercase quit

# Alice sends mixed-case 'QuiT'
C1 SEND QuiT :Mixed case quit
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT
