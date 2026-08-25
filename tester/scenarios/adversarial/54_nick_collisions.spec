# NICK command edge cases and collision scenarios
# Tests nick changes, duplicates, and invalid formats

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali021
C1 SEND USER ali021 0 * :Ali021
C1 EXPECT 001 Ali021 :*

C2 SEND PASS 1234
C2 SEND NICK Bob021
C2 SEND USER bob021 0 * :Bob021
C2 EXPECT 001 Bob021 :*

# Test 1: Change nick to valid name
C1 SEND NICK AliV2021
C1 EXPECT :Ali021!ali021@* NICK :AliV2021
C2 EXPECT_CONNECTED

# Test 2: Try to take existing nick
C1 SEND NICK Bob021
C1 EXPECT 433 AliV2021 Bob021 :*

# Test 3: Nick with special characters (may fail)
C1 SEND NICK Ali021@#$
C1 EXPECT_CONNECTED

# Test 4: Empty nick
C1 SEND NICK
C1 EXPECT_CONNECTED

# Test 5: Very long nick
C1 SEND NICK VeryLongNicknameThatExceedsNormalLimit1234567890abcdefghijklmnop
C1 EXPECT_CONNECTED

# Test 6: Nick change affects channel broadcasts
C3 SEND PASS 1234
C3 SEND NICK Cha021
C3 SEND USER cha021 0 * :Cha021
C3 EXPECT 001 Cha021 :*

C1 SEND JOIN #channel
C1 EXPECT :*!* JOIN #channel
C3 SEND JOIN #channel
C3 EXPECT :Cha021!cha021@* JOIN #channel

# C1 changes nick in channel
C1 SEND NICK FinalAli
C1 EXPECT_CONNECTED

# Test 7: Nick taken immediately after release
C2 SEND NICK AliV2021
C2 EXPECT_CONNECTED

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
