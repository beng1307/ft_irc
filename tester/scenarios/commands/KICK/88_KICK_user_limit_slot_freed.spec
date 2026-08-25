# 88_KICK_user_limit_slot_freed.spec
# Tests that kicking a member from a full channel (+l) frees a member slot, allowing a waiting user to join.
CLIENTS C1, C2, C3

# Alice registers, creates #limited, and sets +l 2
C1 SEND PASS 1234
C1 SEND NICK Ali143
C1 SEND USER ali143 0 * :Ali143
C1 EXPECT 001 Ali143 :*
C1 SEND JOIN #limited
C1 EXPECT :Ali143!* JOIN #limited
C1 SEND MODE #limited +l 2
C1 EXPECT :Ali143!* MODE #limited +l 2

# Bob registers and joins #limited (channel is now full: 2/2)
C2 SEND PASS 1234
C2 SEND NICK Bob143
C2 SEND USER bob143 0 * :Bob143
C2 EXPECT 001 Bob143 :*
C2 SEND JOIN #limited
C2 EXPECT :Bob143!* JOIN #limited
C1 WAIT_RECV :Bob143!* JOIN #limited

# Charlie registers and tries to join full channel
C3 SEND PASS 1234
C3 SEND NICK Cha143
C3 SEND USER cha143 0 * :Cha143
C3 EXPECT 001 Cha143 :*
C3 SEND JOIN #limited
C3 EXPECT 471 Cha143 #limited :Cannot join channel (+l)

# Alice kicks Bob, freeing 1 slot
C1 SEND KICK #limited Bob143 :Room for Cha143
C1 EXPECT :Ali143!* KICK #limited Bob143 :Room for Cha143
C2 EXPECT :Ali143!* KICK #limited Bob143 :Room for Cha143

# Charlie joins successfully
C3 SEND JOIN #limited
C3 EXPECT :Cha143!* JOIN #limited
C1 WAIT_RECV :Cha143!* JOIN #limited
