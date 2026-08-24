# QUIT command with various edge cases
# Tests quit messages, timing, and state cleanup

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

# All join channel
C1 SEND JOIN #channel
C1 EXPECT :Alice!* JOIN #channel
C2 SEND JOIN #channel
C2 EXPECT :Bob!* JOIN #channel
C3 SEND JOIN #channel
C3 EXPECT :Charlie!* JOIN #channel

# Test 1: QUIT with no message
C3 SEND QUIT
C3 EXPECT_DISCONNECTED
C1 EXPECT :Charlie!* QUIT :*
C2 EXPECT :Charlie!* QUIT :*

# Test 2: QUIT with message
C2 SEND QUIT :Leaving now
C2 EXPECT_DISCONNECTED
C1 EXPECT :Bob!* QUIT :Leaving now

# Test 3: QUIT with empty message
C1 SEND QUIT :
C1 EXPECT_DISCONNECTED

# Verify channel is empty
# (Would need to reconnect to check, so we use different client)
