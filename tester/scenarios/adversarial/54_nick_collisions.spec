# NICK command edge cases and collision scenarios
# Tests nick changes, duplicates, and invalid formats

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Test 1: Change nick to valid name
C1 SEND NICK AliceV2
C1 EXPECT :Alice!alice@* NICK :AliceV2
C2 EXPECT_CONNECTED

# Test 2: Try to take existing nick
C1 SEND NICK Bob
C1 EXPECT 433 AliceV2 Bob :*

# Test 3: Nick with special characters (may fail)
C1 SEND NICK Alice@#$
C1 EXPECT_CONNECTED

# Test 4: Empty nick
C1 SEND NICK
C1 EXPECT_CONNECTED

# Test 5: Very long nick
C1 SEND NICK VeryLongNicknameThatExceedsNormalLimit1234567890abcdefghijklmnop
C1 EXPECT_CONNECTED

# Test 6: Nick change affects channel broadcasts
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

C1 SEND JOIN #channel
C1 EXPECT :*!* JOIN #channel
C3 SEND JOIN #channel
C3 EXPECT :Charlie!charlie@* JOIN #channel

# C1 changes nick in channel
C1 SEND NICK FinalAlice
C1 EXPECT_CONNECTED

# Test 7: Nick taken immediately after release
C2 SEND NICK AliceV2
C2 EXPECT_CONNECTED

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
