# MODE with negative user limit should fail or be treated as 0.
# Tests parameter validation for numeric mode arguments.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali054
C1 SEND USER ali054 0 * :Ali054
C1 EXPECT 001 Ali054 :*

C2 SEND PASS 1234
C2 SEND NICK Bob054
C2 SEND USER bob054 0 * :Bob054
C2 EXPECT 001 Bob054 :*

C1 SEND JOIN #limitchannel
C1 EXPECT :Ali054!* JOIN #limitchannel

# Set valid limit first
C1 SEND MODE #limitchannel +l 10
C1 EXPECT :Ali054!* MODE #limitchannel +l 10

# Try to set negative limit (should be rejected or treated as invalid)
C1 SEND MODE #limitchannel +l -5
# Server should either reject with error or treat -5 as invalid
C1 EXPECT_CONNECTED

# Clear limit to verify state
C1 SEND MODE #limitchannel -l
C1 EXPECT :Ali054!* MODE #limitchannel -l

# Verify channel state is still valid
C1 SEND MODE #limitchannel
C1 EXPECT 324 Ali054 #limitchannel *

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
