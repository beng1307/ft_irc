# MODE +l with very large limit (edge of integer range).
# Tests if server validates realistic limits.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #biglimit
C1 EXPECT :Alice!* JOIN #biglimit

# Set very large limit (near 32-bit int max)
C1 SEND MODE #biglimit +l 2147483647
# Should accept or cap at reasonable value
C1 EXPECT_CONNECTED

# Verify limit is set
C1 SEND MODE #biglimit
C1 EXPECT 324 Alice #biglimit +l *

# Try to set limit larger than 32-bit
C1 SEND MODE #biglimit +l 9999999999
# Server should either reject or truncate
C1 EXPECT_CONNECTED

# Set reasonable limit
C1 SEND MODE #biglimit +l 100
C1 EXPECT :Alice!* MODE #biglimit +l 100

# Verify it took effect
C1 SEND MODE #biglimit
C1 EXPECT 324 Alice #biglimit +l 100

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
