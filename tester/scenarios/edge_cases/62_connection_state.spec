# Connection state machine edge cases
# Tests unregistered client restrictions and state transitions

CLIENTS C1, C2

# Test 1: Send command before PASS (server may just ignore or queue it)
C1 SEND NICK Ali417
C1 EXPECT_CONNECTED

# Test 2: Complete registration (PASS first)
C1 SEND PASS 1234
C1 SEND NICK Ali417
C1 SEND USER ali417 0 * :Ali417
C1 EXPECT 001 Ali417 :*

# Test 3: Change nick after registration
C1 SEND NICK AliV2417
C1 EXPECT :Ali417!ali417@* NICK :AliV2417

# Test 4: Send USER again (should fail or be ignored)
C1 SEND USER ali417 0 * :Ali417
# Server may accept, ignore, or error - all valid
C1 EXPECT_CONNECTED

# Test 5: Double PASS (should be ignored if already auth'd)
C1 SEND PASS 1234
C1 EXPECT_CONNECTED

# Test 6: Unregistered client tries to JOIN
C2 SEND NICK Bob417
C2 EXPECT_CONNECTED

# Test 7: Unregistered client tries MODE
C2 SEND MODE #channel +i
C2 EXPECT_CONNECTED

# Test 8: Register C2 properly
C2 SEND PASS 1234
C2 SEND NICK Bob417
C2 SEND USER bob417 0 * :Bob417
C2 EXPECT 001 Bob417 :*

# Test 9: Now C2 can JOIN
C2 SEND JOIN #channel
C2 EXPECT :Bob417!* JOIN #channel

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED

