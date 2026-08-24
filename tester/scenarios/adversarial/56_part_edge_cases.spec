# PART command edge cases
# Tests part messages, invalid channels, and state cleanup

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
C1 SEND JOIN #test
C1 EXPECT :Alice!* JOIN #test
C2 SEND JOIN #test
C2 EXPECT :Bob!* JOIN #test

# Test 1: PART with no channel
C1 SEND PART
C1 EXPECT 461 Alice PART :*

# Test 2: PART non-existent channel
C1 SEND PART #nonexistent
C1 EXPECT 403 Alice #nonexistent :*

# Test 3: PART with message
C1 SEND PART #test :Gotta go!
C1 EXPECT :Alice!* PART #test :Gotta go!
C2 EXPECT :Alice!* PART #test :Gotta go!

# Test 4: PART already left channel
C1 SEND PART #test
C1 EXPECT 442 Alice #test :*

# Test 5: Multiple PARTs in quick succession
C2 SEND JOIN #test2
C2 EXPECT :Bob!* JOIN #test2
C2 SEND PART #test2
C2 EXPECT :Bob!* PART #test2
C2 SEND PART #test2
C2 EXPECT 403 Bob #test2 :*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
