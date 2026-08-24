# MODE +k with empty key parameter.
# Edge case: +k should require a non-empty key.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #emptykey
C1 EXPECT :Alice!* JOIN #emptykey

# Try to set key to empty string: +k with no parameter
C1 SEND MODE #emptykey +k
# Should error: missing parameter
C1 EXPECT 461 Alice MODE :Not enough parameters

# Try with explicit empty (sending just whitespace)
C1 SEND_RAW MODE #emptykey +k \r\n
C1 EXPECT_CONNECTED

# Verify no key was set
C1 SEND MODE #emptykey
C1 EXPECT 324 Alice #emptykey *

# Now set a valid key
C1 SEND MODE #emptykey +k mykey
C1 EXPECT :Alice!* MODE #emptykey +k mykey

# Bob must provide key to join
C2 SEND JOIN #emptykey
C2 EXPECT 475 Bob #emptykey :Cannot join channel (+k)

C2 SEND JOIN #emptykey mykey
C2 EXPECT :Bob!* JOIN #emptykey

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
