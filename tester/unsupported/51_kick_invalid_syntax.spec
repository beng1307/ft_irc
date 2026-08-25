# KICK command parser robustness tests
# Tests for malformed KICK commands and edge cases

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

# Create channel with Alice as operator
C1 SEND JOIN #kick_test
C1 EXPECT :Alice!* JOIN #kick_test
C2 SEND JOIN #kick_test
C2 EXPECT :Bob!* JOIN #kick_test
C3 SEND JOIN #kick_test
C3 EXPECT :Charlie!* JOIN #kick_test

# Give Alice operator status
C1 SEND MODE #kick_test +o Alice
C1 EXPECT_CONNECTED

# Test 1: KICK with no channel
C1 SEND KICK Bob
C1 EXPECT 461 Alice KICK :*

# Test 2: KICK with channel but no user
C1 SEND KICK #kick_test
C1 EXPECT 461 Alice KICK :*

# Test 3: KICK with too many spaces
C1 SEND KICK   #kick_test   Bob
C1 EXPECT :Alice!* KICK #kick_test Bob :*

# Test 4: KICK non-existent user
C1 SEND KICK #kick_test Nonexistent
C1 EXPECT_CONNECTED

# Test 5: KICK from channel you're not in
C3 SEND PART #kick_test
C3 EXPECT :Charlie!* PART #kick_test
C1 SEND KICK #kick_test Charlie
C1 EXPECT 441 Alice Charlie #kick_test :*

# Test 6: Valid KICK with reason
C1 SEND KICK #kick_test Bob :Spamming
C2 EXPECT :Alice!* KICK #kick_test Bob :Spamming
C2 EXPECT_DISCONNECTED

# Verify Bob was kicked
C1 SEND NAMES #kick_test
C1 EXPECT 353 Alice = #kick_test :@Alice

C1 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
