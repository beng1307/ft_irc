# Operator privilege escalation and boundary tests
# Tests that non-ops cannot perform privileged operations

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali026
C1 SEND USER ali026 0 * :Ali026
C1 EXPECT 001 Ali026 :*

C2 SEND PASS 1234
C2 SEND NICK Bob026
C2 SEND USER bob026 0 * :Bob026
C2 EXPECT 001 Bob026 :*

C3 SEND PASS 1234
C3 SEND NICK Cha026
C3 SEND USER cha026 0 * :Cha026
C3 EXPECT 001 Cha026 :*

# Create channel with Alice as op
C1 SEND JOIN #restricted
C1 EXPECT :Ali026!* JOIN #restricted

# Test 1: Non-op tries to give ops
C2 SEND JOIN #restricted
C2 EXPECT :Bob026!* JOIN #restricted
C2 SEND MODE #restricted +o Cha026
C2 EXPECT 482 Bob026 #restricted :*

# Test 2: Op gives ops to non-existent user
C1 SEND MODE #restricted +o Nonexistent
C1 EXPECT 401 Ali026 Nonexistent :*

# Test 3: Op gives ops to user not in channel
C3 SEND PASS 1234
C3 SEND PASS 1234
# (C3 is already connected above)
C1 SEND MODE #restricted +o Cha026
C1 EXPECT 441 Ali026 Cha026 #restricted :*

# Test 4: Charlie joins and Alice gives ops
C3 SEND JOIN #restricted
C3 EXPECT :Cha026!* JOIN #restricted
C1 SEND MODE #restricted +o Cha026
C1 EXPECT :Ali026!* MODE #restricted +o Cha026
C3 EXPECT :Ali026!* MODE #restricted +o Cha026

# Test 5: Now Charlie (op) can set modes
C3 SEND MODE #restricted +i
C3 EXPECT :Cha026!* MODE #restricted +i

# Test 6: Bob (non-op) tries to set mode
C2 SEND MODE #restricted -i
C2 EXPECT 482 Bob026 #restricted :*

# Test 7: Non-op tries to kick
C2 SEND KICK #restricted Ali026
C2 EXPECT 482 Bob026 #restricted :*

# Test 8: Op can kick
C1 SEND KICK #restricted Bob026 :Privileges test
C2 EXPECT :Ali026!* KICK #restricted Bob026 :Privileges test
C2 EXPECT_DISCONNECTED

C1 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
