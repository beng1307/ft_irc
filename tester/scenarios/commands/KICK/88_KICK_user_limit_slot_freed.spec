# 88_KICK_user_limit_slot_freed.spec
# Tests that kicking a member from a full channel (+l) frees a member slot, allowing a waiting user to join.
CLIENTS C1, C2, C3

# Alice registers, creates #limited, and sets +l 2
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #limited
C1 EXPECT :Alice!* JOIN #limited
C1 SEND MODE #limited +l 2
C1 EXPECT :Alice!* MODE #limited +l 2

# Bob registers and joins #limited (channel is now full: 2/2)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*
C2 SEND JOIN #limited
C2 EXPECT :Bob!* JOIN #limited
C1 WAIT_RECV :Bob!* JOIN #limited

# Charlie registers and tries to join full channel
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*
C3 SEND JOIN #limited
C3 EXPECT 471 Charlie #limited :Cannot join channel (+l)

# Alice kicks Bob, freeing 1 slot
C1 SEND KICK #limited Bob :Room for Charlie
C1 EXPECT :Alice!* KICK #limited Bob :Room for Charlie
C2 EXPECT :Alice!* KICK #limited Bob :Room for Charlie

# Charlie joins successfully
C3 SEND JOIN #limited
C3 EXPECT :Charlie!* JOIN #limited
C1 WAIT_RECV :Charlie!* JOIN #limited
