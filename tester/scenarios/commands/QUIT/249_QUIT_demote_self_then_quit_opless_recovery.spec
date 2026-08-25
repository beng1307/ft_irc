# 249_QUIT_demote_self_then_quit_opless_recovery.spec
# Tests that if a sole operator de-ops themselves (leaving channel opless) and then quits, the server auto-promotes the next member.
CLIENTS C1, C2

# Alice (op) and Bob (regular)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #opless
C1 EXPECT :Alice!* JOIN #opless

C2 SEND JOIN #opless
C2 WAIT_RECV :Bob!* JOIN #opless
C1 WAIT_RECV :Bob!* JOIN #opless

# Alice demotes herself from operator -> channel is now opless
C1 SEND MODE #opless -o Alice
C1 EXPECT :Alice!* MODE #opless -o Alice
C2 WAIT_RECV :Alice!* MODE #opless -o Alice

# Alice quits -> Server auto-promotes Bob
C1 SEND QUIT :Goodbye
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

C2 WAIT_RECV :Alice!* QUIT :Goodbye

# Bob verifies operator status by setting invite-only mode
C2 SEND MODE #opless +i
C2 EXPECT :Bob!* MODE #opless +i
