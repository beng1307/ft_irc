# 65_INVITE_key_and_limit_retry_preservation.spec
# Tests that a failed JOIN attempt due to channel key (+k) or limit (+l) does NOT consume the invitation.
# Expected: Client can retry JOIN with the correct key and successfully enter the +i channel.
CLIENTS C1, C2

# Alice63 creates +i and +k channel
C1 SEND PASS 1234
C1 SEND NICK Ali090
C1 SEND USER ali090 0 * :Ali090
C1 EXPECT 001 Ali090 :*
C1 SEND JOIN #locked63
C1 EXPECT :Ali090!* JOIN #locked63
C1 SEND MODE #locked63 +ik pass123
C1 EXPECT :Ali090!* MODE #locked63 +ik pass123

# Bob63 registers
C2 SEND PASS 1234
C2 SEND NICK Bob090
C2 SEND USER bob090 0 * :Bob090
C2 EXPECT 001 Bob090 :*

# Alice63 invites Bob63
C1 SEND INVITE Bob090 #locked63
C1 EXPECT 341 Ali090 Bob090 #locked63
C2 WAIT_RECV :Ali090!* INVITE Bob090 :#locked63

# Bob63 attempts to join without the required key
C2 SEND JOIN #locked63
C2 EXPECT 475 Bob090 #locked63 :Cannot join channel (+k)

# Bob63 retries JOIN with correct key (invite must still be valid)
C2 SEND JOIN #locked63 pass123
C2 WAIT_RECV :Bob090!* JOIN #locked63
C1 WAIT_RECV :Bob090!* JOIN #locked63
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
