# MODE +k with special characters in key.
# Tests if channel keys preserve special characters and spaces.

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

C1 SEND JOIN #keychannel
C1 EXPECT :Alice!* JOIN #keychannel

# Set key with special characters
C1 SEND MODE #keychannel +k p@ssw0rd!
C1 EXPECT :Alice!* MODE #keychannel +k p@ssw0rd!

# Bob tries with wrong key
C2 SEND JOIN #keychannel wrongkey
C2 EXPECT 475 Bob #keychannel :Cannot join channel (+k)

# Bob tries with correct key
C2 SEND JOIN #keychannel p@ssw0rd!
C2 EXPECT :Bob!* JOIN #keychannel

# Charlie tries different format
C3 SEND JOIN #keychannel p@ssw0rd!
C3 EXPECT :Charlie!* JOIN #keychannel

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
