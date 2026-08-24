# Operator privilege escalation and boundary tests
# Tests that non-ops cannot perform privileged operations

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

# Create channel with Alice as op
C1 SEND JOIN #restricted
C1 EXPECT :Alice!* JOIN #restricted

# Test 1: Non-op tries to give ops
C2 SEND JOIN #restricted
C2 EXPECT :Bob!* JOIN #restricted
C2 SEND MODE #restricted +o Charlie
C2 EXPECT 482 Bob #restricted :*

# Test 2: Op gives ops to non-existent user
C1 SEND MODE #restricted +o Nonexistent
C1 EXPECT 401 Alice Nonexistent :*

# Test 3: Op gives ops to user not in channel
C3 SEND PASS 1234
C3 SEND PASS 1234
# (C3 is already connected above)
C1 SEND MODE #restricted +o Charlie
C1 EXPECT 441 Alice Charlie #restricted :*

# Test 4: Charlie joins and Alice gives ops
C3 SEND JOIN #restricted
C3 EXPECT :Charlie!* JOIN #restricted
C1 SEND MODE #restricted +o Charlie
C1 EXPECT :Alice!* MODE #restricted +o Charlie
C3 EXPECT :Alice!* MODE #restricted +o Charlie

# Test 5: Now Charlie (op) can set modes
C3 SEND MODE #restricted +i
C3 EXPECT :Charlie!* MODE #restricted +i

# Test 6: Bob (non-op) tries to set mode
C2 SEND MODE #restricted -i
C2 EXPECT 482 Bob #restricted :*

# Test 7: Non-op tries to kick
C2 SEND KICK #restricted Alice
C2 EXPECT 482 Bob #restricted :*

# Test 8: Op can kick
C1 SEND KICK #restricted Bob :Privileges test
C2 EXPECT :Alice!* KICK #restricted Bob :Privileges test
C2 EXPECT_DISCONNECTED

C1 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
