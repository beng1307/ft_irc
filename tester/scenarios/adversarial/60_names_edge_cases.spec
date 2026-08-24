# NAMES command with various edge cases
# Tests NAMES response with different channel states

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

# Create channel and join
C1 SEND JOIN #test
C1 EXPECT :Alice!* JOIN #test

# Add more users
C2 SEND JOIN #test
C2 EXPECT :Bob!* JOIN #test
C3 SEND JOIN #test
C3 EXPECT :Charlie!* JOIN #test

# Test NAMES command
C1 SEND NAMES #test
C1 EXPECT 353 Alice = #test :*
C1 EXPECT 366 Alice #test :*

# Test NAMES for non-existent channel
C1 SEND NAMES #nonexistent
C1 EXPECT_CONNECTED

# Test all clients are connected
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
