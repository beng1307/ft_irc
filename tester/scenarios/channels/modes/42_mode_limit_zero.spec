# MODE +l 0 should be treated as "no limit" or error.
# Edge case: numeric boundary condition.

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

C1 SEND JOIN #zerolimit
C1 EXPECT :Alice!* JOIN #zerolimit

# Set limit to 0 (edge case)
C1 SEND MODE #zerolimit +l 0
# Server should accept or reject; either is valid behavior
C1 EXPECT_CONNECTED

# Try to join with "no limit" (Alice is creator, gets in anyway)
C2 SEND JOIN #zerolimit
C2 EXPECT_CONNECTED

# Try third user
C3 SEND JOIN #zerolimit
C3 EXPECT_CONNECTED

# Verify channel is still operational
C1 SEND PRIVMSG #zerolimit :Channel works
C2 WAIT_RECV :Alice!* PRIVMSG #zerolimit :Channel works
C3 WAIT_RECV :Alice!* PRIVMSG #zerolimit :Channel works

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
