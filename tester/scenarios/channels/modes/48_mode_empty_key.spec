# MODE +k with empty key parameter.
# Edge case: +k should require a non-empty key.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali061
C1 SEND USER ali061 0 * :Ali061
C1 EXPECT 001 Ali061 :*

C2 SEND PASS 1234
C2 SEND NICK Bob061
C2 SEND USER bob061 0 * :Bob061
C2 EXPECT 001 Bob061 :*

C1 SEND JOIN #emptykey
C1 EXPECT :Ali061!* JOIN #emptykey

# Try to set key to empty string: +k with no parameter
C1 SEND MODE #emptykey +k
# Should error: missing parameter
C1 EXPECT 461 Ali061 MODE :Not enough parameters

# Try with explicit empty (sending just whitespace)
C1 SEND_RAW MODE #emptykey +k \r\n
C1 EXPECT_CONNECTED

# Verify no key was set
C1 SEND MODE #emptykey
C1 EXPECT 324 Ali061 #emptykey *

# Now set a valid key
C1 SEND MODE #emptykey +k mykey
C1 EXPECT :Ali061!* MODE #emptykey +k mykey

# Bob must provide key to join
C2 SEND JOIN #emptykey
C2 EXPECT 475 Bob061 #emptykey :Cannot join channel (+k)

C2 SEND JOIN #emptykey mykey
C2 EXPECT :Bob061!* JOIN #emptykey

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
