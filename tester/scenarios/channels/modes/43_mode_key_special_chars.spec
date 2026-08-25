# MODE +k with special characters in key.
# Tests if channel keys preserve special characters and spaces.

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali056
C1 SEND USER ali056 0 * :Ali056
C1 EXPECT 001 Ali056 :*

C2 SEND PASS 1234
C2 SEND NICK Bob056
C2 SEND USER bob056 0 * :Bob056
C2 EXPECT 001 Bob056 :*

C3 SEND PASS 1234
C3 SEND NICK Cha056
C3 SEND USER cha056 0 * :Cha056
C3 EXPECT 001 Cha056 :*

C1 SEND JOIN #keychannel
C1 EXPECT :Ali056!* JOIN #keychannel

# Set key with special characters
C1 SEND MODE #keychannel +k p@ssw0rd!
C1 EXPECT :Ali056!* MODE #keychannel +k p@ssw0rd!

# Bob tries with wrong key
C2 SEND JOIN #keychannel wrongkey
C2 EXPECT 475 Bob056 #keychannel :Cannot join channel (+k)

# Bob tries with correct key
C2 SEND JOIN #keychannel p@ssw0rd!
C2 EXPECT :Bob056!* JOIN #keychannel

# Charlie tries different format
C3 SEND JOIN #keychannel p@ssw0rd!
C3 EXPECT :Cha056!* JOIN #keychannel

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
