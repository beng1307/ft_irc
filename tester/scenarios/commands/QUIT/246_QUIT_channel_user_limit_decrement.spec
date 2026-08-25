# 246_QUIT_channel_user_limit_decrement.spec
# Tests that when a member quits a channel with +l limit, the member count decrements and allows a blocked user to enter.
CLIENTS C1, C2, C3

# Alice (C1) and Bob (C2)
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

# Alice creates #capacity and sets limit to 2
C1 SEND JOIN #capacity
C1 EXPECT :Alice!* JOIN #capacity
C1 SEND MODE #capacity +l 2
C1 EXPECT :Alice!* MODE #capacity +l 2

# Bob joins (channel is now 2/2 full)
C2 SEND JOIN #capacity
C2 WAIT_RECV :Bob!* JOIN #capacity
C1 WAIT_RECV :Bob!* JOIN #capacity

# Charlie attempts to join -> blocked with 471 ERR_CHANNELISFULL
C3 SEND JOIN #capacity
C3 EXPECT 471 Charlie #capacity :Cannot join channel (+l)

# Alice quits -> occupancy drops to 1/2
C1 SEND QUIT :Freeing slot
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

C2 WAIT_RECV :Alice!* QUIT :Freeing slot

# Charlie now attempts to join -> succeeds
C3 SEND JOIN #capacity
C3 EXPECT :Charlie!* JOIN #capacity
