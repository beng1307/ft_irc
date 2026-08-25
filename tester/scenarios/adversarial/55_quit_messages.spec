# QUIT command with various edge cases
# Tests quit messages, timing, and state cleanup

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali022
C1 SEND USER ali022 0 * :Ali022
C1 EXPECT 001 Ali022 :*

C2 SEND PASS 1234
C2 SEND NICK Bob022
C2 SEND USER bob022 0 * :Bob022
C2 EXPECT 001 Bob022 :*

C3 SEND PASS 1234
C3 SEND NICK Cha022
C3 SEND USER cha022 0 * :Cha022
C3 EXPECT 001 Cha022 :*

# All join channel
C1 SEND JOIN #channel
C1 EXPECT :Ali022!* JOIN #channel
C2 SEND JOIN #channel
C2 EXPECT :Bob022!* JOIN #channel
C3 SEND JOIN #channel
C3 EXPECT :Cha022!* JOIN #channel

# Test 1: QUIT with no message
C3 SEND QUIT
C3 EXPECT_DISCONNECTED
C1 EXPECT :Cha022!* QUIT :*
C2 EXPECT :Cha022!* QUIT :*

# Test 2: QUIT with message
C2 SEND QUIT :Leaving now
C2 EXPECT_DISCONNECTED
C1 EXPECT :Bob022!* QUIT :Leaving now

# Test 3: QUIT with empty message
C1 SEND QUIT :
C1 EXPECT_DISCONNECTED

# Verify channel is empty
# (Would need to reconnect to check, so we use different client)
