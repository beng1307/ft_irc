# TOPIC command edge cases and parser robustness
# Tests TOPIC command with various edge cases

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Create channel
C1 SEND JOIN #topic_test
C1 EXPECT :Alice!* JOIN #topic_test
C2 SEND JOIN #topic_test
C2 EXPECT :Bob!* JOIN #topic_test

# Test 1: TOPIC with no channel
C1 SEND TOPIC
C1 EXPECT 461 Alice TOPIC :*

# Test 2: Query topic (no changes yet)
C1 SEND TOPIC #topic_test
C1 EXPECT 331 Alice #topic_test :*

# Test 3: Set topic with empty string
C1 SEND TOPIC #topic_test :
C1 EXPECT :Alice!* TOPIC #topic_test :
C2 EXPECT :Alice!* TOPIC #topic_test :

# Test 4: Verify topic was cleared
C1 SEND TOPIC #topic_test
C1 EXPECT 331 Alice #topic_test :*

# Test 5: Set topic with long string (tested with special chars within max topic length)
C1 SEND TOPIC #topic_test :This is a long topic testing special chars !@#$%^&*()-=+[]{};:'",.<>/?|\ and boundary limits within topic length limit.
C1 EXPECT :Alice!* TOPIC #topic_test :*

# Test 6: Query topic and verify it was set
C1 SEND TOPIC #topic_test
C1 EXPECT 332 Alice #topic_test :*

# Test 7: Non-op tries to change topic (may succeed depending on server)
C2 SEND TOPIC #topic_test :Bob's topic
# Server may allow or reject - both are valid
C2 EXPECT_CONNECTED

# Test 8: TOPIC on non-existent channel
C1 SEND TOPIC #nonexistent :test
C1 EXPECT 403 Alice #nonexistent :*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
