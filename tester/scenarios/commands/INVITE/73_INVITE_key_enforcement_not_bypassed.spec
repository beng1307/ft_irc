# 73_INVITE_key_enforcement_not_bypassed.spec
# Tests that an invitation satisfies +i but does NOT bypass channel password keys (+k).
# Expected: An invited client attempting to join without the required channel key is rejected with 475 ERR_BADCHANNELKEY.
CLIENTS C1, C2

# Alice creates +i and +k channel
C1 SEND PASS 1234
C1 SEND NICK Alice73
C1 SEND USER alice73 0 * :Alice
C1 EXPECT 001 Alice73 :*
C1 SEND JOIN #keychan73
C1 EXPECT :Alice73!* JOIN #keychan73
C1 SEND MODE #keychan73 +ik secret999
C1 EXPECT :Alice73!* MODE #keychan73 +ik secret999

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob73
C2 SEND USER bob73 0 * :Bob
C2 EXPECT 001 Bob73 :*

# Alice invites Bob
C1 SEND INVITE Bob73 #keychan73
C1 EXPECT 341 Alice73 Bob73 #keychan73
C2 WAIT_RECV :Alice73!* INVITE Bob73 :#keychan73

# Bob attempts to join without the key
C2 SEND JOIN #keychan73
C2 EXPECT 475 Bob73 #keychan73 :Cannot join channel (+k)

# Bob attempts to join with the WRONG key
C2 SEND JOIN #keychan73 wrongkey
C2 EXPECT 475 Bob73 #keychan73 :Cannot join channel (+k)

# Bob attempts to join with the CORRECT key -> Success
C2 SEND JOIN #keychan73 secret999
C2 WAIT_RECV :Bob73!* JOIN #keychan73
C1 WAIT_RECV :Bob73!* JOIN #keychan73
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
