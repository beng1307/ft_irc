# PART command edge cases
# Tests part messages, invalid channels, and state cleanup

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali023
C1 SEND USER ali023 0 * :Ali023
C1 EXPECT 001 Ali023 :*

C2 SEND PASS 1234
C2 SEND NICK Bob023
C2 SEND USER bob023 0 * :Bob023
C2 EXPECT 001 Bob023 :*

# Create channel
C1 SEND JOIN #test
C1 EXPECT :Ali023!* JOIN #test
C2 SEND JOIN #test
C2 EXPECT :Bob023!* JOIN #test

# Test 1: PART with no channel
C1 SEND PART
C1 EXPECT 461 Ali023 PART :*

# Test 2: PART non-existent channel
C1 SEND PART #nonexistent
C1 EXPECT 403 Ali023 #nonexistent :*

# Test 3: PART with message
C1 SEND PART #test :Gotta go!
C1 EXPECT :Ali023!* PART #test :Gotta go!
C2 EXPECT :Ali023!* PART #test :Gotta go!

# Test 4: PART already left channel
C1 SEND PART #test
C1 EXPECT 442 Ali023 #test :*

# Test 5: Multiple PARTs in quick succession
C2 SEND JOIN #test2
C2 EXPECT :Bob023!* JOIN #test2
C2 SEND PART #test2
C2 EXPECT :Bob023!* PART #test2
C2 SEND PART #test2
C2 EXPECT 403 Bob023 #test2 :*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
