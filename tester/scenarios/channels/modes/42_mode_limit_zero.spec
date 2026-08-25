# MODE +l 0 should be treated as "no limit" or error.
# Edge case: numeric boundary condition.

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali421
C1 SEND USER ali421 0 * :Ali421
C1 EXPECT 001 Ali421 :*

C2 SEND PASS 1234
C2 SEND NICK Bob421
C2 SEND USER bob421 0 * :Bob421
C2 EXPECT 001 Bob421 :*

C3 SEND PASS 1234
C3 SEND NICK Cha421
C3 SEND USER cha421 0 * :Cha421
C3 EXPECT 001 Cha421 :*

C1 SEND JOIN #zerolimit
C1 EXPECT :Ali421!* JOIN #zerolimit

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
C2 WAIT_RECV :Ali421!* PRIVMSG #zerolimit :Channel works
C3 WAIT_RECV :Ali421!* PRIVMSG #zerolimit :Channel works

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
