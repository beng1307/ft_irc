# NAMES command with various edge cases
# Tests NAMES response with different channel states

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali027
C1 SEND USER ali027 0 * :Ali027
C1 EXPECT 001 Ali027 :*

C2 SEND PASS 1234
C2 SEND NICK Bob027
C2 SEND USER bob027 0 * :Bob027
C2 EXPECT 001 Bob027 :*

C3 SEND PASS 1234
C3 SEND NICK Cha027
C3 SEND USER cha027 0 * :Cha027
C3 EXPECT 001 Cha027 :*

# Create channel and join
C1 SEND JOIN #test
C1 EXPECT :Ali027!* JOIN #test

# Add more users
C2 SEND JOIN #test
C2 EXPECT :Bob027!* JOIN #test
C3 SEND JOIN #test
C3 EXPECT :Cha027!* JOIN #test

# Test NAMES command
C1 SEND NAMES #test
C1 EXPECT 353 Ali027 = #test :*
C1 EXPECT 366 Ali027 #test :*

# Test NAMES for non-existent channel
C1 SEND NAMES #nonexistent
C1 EXPECT_CONNECTED

# Test all clients are connected
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
