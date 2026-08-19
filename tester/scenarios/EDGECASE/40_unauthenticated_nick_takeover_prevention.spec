# Scenario 40: Unauthenticated Nick Takeover & Out of Order Registration
# Tests state transitions when NICK/USER are sent before PASS vs another client registering
CLIENTS C1, C2

# C1 sends NICK without PASS
C1 SEND NICK Alice
# C1 is not registered yet, sending JOIN fails with 451
C1 SEND JOIN #room
C1 EXPECT 451 * :You have not registered

# C2 connects with valid credentials
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 completes registration with PASS and USER
C1 SEND PASS 1234
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Now C1 can join channels
C1 SEND JOIN #room
C1 EXPECT :Alice!* JOIN #room
