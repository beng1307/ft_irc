# MODE with negative user limit should fail or be treated as 0.
# Tests parameter validation for numeric mode arguments.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #limitchannel
C1 EXPECT :Alice!* JOIN #limitchannel

# Set valid limit first
C1 SEND MODE #limitchannel +l 10
C1 EXPECT :Alice!* MODE #limitchannel +l 10

# Try to set negative limit (should be rejected or treated as invalid)
C1 SEND MODE #limitchannel +l -5
# Server should either reject with error or treat -5 as invalid
C1 EXPECT_CONNECTED

# Clear limit to verify state
C1 SEND MODE #limitchannel -l
C1 EXPECT :Alice!* MODE #limitchannel -l

# Verify channel state is still valid
C1 SEND MODE #limitchannel
C1 EXPECT 324 Alice #limitchannel *

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
