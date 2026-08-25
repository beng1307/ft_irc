# 72_INVITE_limit_saturation_blocks_invited_user.spec
# Tests that an invitation satisfies +i but does NOT bypass channel user capacity limits (+l).
# Expected: An invited client attempting to join a full (+l) channel is rejected with 471 ERR_CHANNELISFULL.
CLIENTS C1, C2, C3

# Alice creates +i +l 2 channel (capacity 2: Alice + 1 more)
C1 SEND PASS 1234
C1 SEND NICK Ali097
C1 SEND USER ali097 0 * :Ali097
C1 EXPECT 001 Ali097 :*
C1 SEND JOIN #fullroom72
C1 EXPECT :Ali097!* JOIN #fullroom72
C1 SEND MODE #fullroom72 +il 2
C1 EXPECT :Ali097!* MODE #fullroom72 +il 2

# Bob and Charlie register
C2 SEND PASS 1234
C2 SEND NICK Bob097
C2 SEND USER bob097 0 * :Bob097
C2 EXPECT 001 Bob097 :*

C3 SEND PASS 1234
C3 SEND NICK Cha097
C3 SEND USER cha097 0 * :Cha097
C3 EXPECT 001 Cha097 :*

# Alice invites both Bob and Charlie
C1 SEND INVITE Bob097 #fullroom72
C1 EXPECT 341 Ali097 Bob097 #fullroom72
C2 WAIT_RECV :Ali097!* INVITE Bob097 :#fullroom72

C1 SEND INVITE Cha097 #fullroom72
C1 EXPECT 341 Ali097 Cha097 #fullroom72
C3 WAIT_RECV :Ali097!* INVITE Cha097 :#fullroom72

# Bob joins -> Channel reaches capacity (2 members)
C2 SEND JOIN #fullroom72
C2 WAIT_RECV :Bob097!* JOIN #fullroom72

# Charlie attempts to join with valid invite -> Blocked by user limit (+l)
C3 SEND JOIN #fullroom72
C3 EXPECT 471 Cha097 #fullroom72 :Cannot join channel (+l)

# Bob parts -> Capacity frees up
C2 SEND PART #fullroom72 :bye
C1 WAIT_RECV :Bob097!* PART #fullroom72*

# Charlie retries -> Join succeeds using preserved invitation
C3 SEND JOIN #fullroom72
C3 WAIT_RECV :Cha097!* JOIN #fullroom72
C1 WAIT_RECV :Cha097!* JOIN #fullroom72
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
