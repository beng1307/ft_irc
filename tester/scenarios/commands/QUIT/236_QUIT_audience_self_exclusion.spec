# 209_QUIT_audience_self_exclusion.spec
# Tests that the quitting client does not receive their own QUIT broadcast message echo.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali324
C1 SEND USER ali324 0 * :Ali324
C1 EXPECT 001 Ali324 :*

C1 SEND JOIN #lobby
C1 EXPECT :Ali324!* JOIN #lobby

# Alice quits: must ONLY receive ERROR :Closing connection, never :Alice!* QUIT
C1 SEND QUIT :I am out
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT
