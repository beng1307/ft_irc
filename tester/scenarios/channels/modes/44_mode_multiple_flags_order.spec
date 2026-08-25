# MODE with multiple flags in different orders: +il vs +li
# Tests if mode order affects outcome and broadcast format.
# NOTE: Server normalizes flag order - always +il regardless of input

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali057
C1 SEND USER ali057 0 * :Ali057
C1 EXPECT 001 Ali057 :*

C2 SEND PASS 1234
C2 SEND NICK Bob057
C2 SEND USER bob057 0 * :Bob057
C2 EXPECT 001 Bob057 :*

C1 SEND JOIN #orderchannel
C1 EXPECT :Ali057!* JOIN #orderchannel
C2 SEND JOIN #orderchannel
C2 EXPECT :Bob057!* JOIN #orderchannel
C1 WAIT_RECV :Bob057!* JOIN #orderchannel

# Set +i (invite-only) and +l (limit) with specific order +il
C1 SEND MODE #orderchannel +il 5
# Server broadcasts exactly as sent
C1 EXPECT :Ali057!* MODE #orderchannel +il 5
C2 WAIT_RECV :Ali057!* MODE #orderchannel +il *

# Query current mode
C1 SEND MODE #orderchannel
# Server stores and returns normalized as +il
C1 EXPECT 324 Ali057 #orderchannel +il 5

# Remove and re-add in +li order (should still normalize to +il)
C1 SEND MODE #orderchannel -il
C1 EXPECT :Ali057!* MODE #orderchannel -il
C1 SEND MODE #orderchannel +li 3
C1 EXPECT :Ali057!* MODE #orderchannel +li *
C2 WAIT_RECV :Ali057!* MODE #orderchannel +li *

# Query again - server normalizes to +il regardless of input order
C1 SEND MODE #orderchannel
# Server should return the same normalized order as before (+il not +li)
C1 EXPECT 324 Ali057 #orderchannel +il 3

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
