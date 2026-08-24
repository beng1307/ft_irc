# JOIN command with multiple edge cases
# Tests parser robustness, channel limits, and key handling

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

# Test 1: JOIN with no channel
C1 SEND JOIN
C1 EXPECT 461 Alice JOIN :*

# Test 2: JOIN multiple channels (comma-separated)
C1 SEND JOIN #one,#two,#three
# Server should handle or reject based on implementation
C1 EXPECT_CONNECTED

# Test 3: JOIN with channel key
C1 SEND JOIN #keyed_channel test_key
C1 EXPECT :Alice!* JOIN #keyed_channel

# Test 4: Try to join with wrong key
C2 SEND JOIN #keyed_channel wrong_key
C2 EXPECT_CONNECTED

# Test 5: Join with correct key
C2 SEND JOIN #keyed_channel test_key
C2 EXPECT :Bob!* JOIN #keyed_channel

# Test 6: Join again (already member)
C1 SEND JOIN #keyed_channel test_key
# Server should just acknowledge, user already in channel
C1 EXPECT_CONNECTED

# Test 7: JOIN channel with special characters in name
C1 SEND JOIN #test-channel_123
C1 EXPECT :Alice!* JOIN #test-channel_123

# Test 8: JOIN with very long channel name
C1 SEND JOIN #thisIsAVeryLongChannelNameThatMightExceedLimits1234567890
C1 EXPECT_CONNECTED

# Test 9: JOIN non-existent channel (creates it)
C3 SEND JOIN #new_channel
C3 EXPECT :Charlie!* JOIN #new_channel

# Test 10: Verify channel was created and C3 is operator
C3 SEND NAMES #new_channel
C3 EXPECT 353 Charlie = #new_channel :@Charlie

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
