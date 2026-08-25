# 202_QUIT_empty_colon_reason.spec
# Tests that QUIT with an empty colon argument broadcasts an empty parameter.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali317
C1 SEND USER ali317 0 * :Ali317
C1 EXPECT 001 Ali317 :*

C2 SEND PASS 1234
C2 SEND NICK Bob317
C2 SEND USER bob317 0 * :Bob317
C2 EXPECT 001 Bob317 :*

C1 SEND JOIN #lobby
C1 EXPECT :Ali317!* JOIN #lobby

C2 SEND JOIN #lobby
C2 WAIT_RECV :Bob317!* JOIN #lobby
C1 WAIT_RECV :Bob317!* JOIN #lobby

# Alice quits with empty colon reason
C1 SEND QUIT :
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives QUIT with empty trailing colon
C2 WAIT_RECV :Ali317!* QUIT :
C2 EXPECT_CONNECTED
