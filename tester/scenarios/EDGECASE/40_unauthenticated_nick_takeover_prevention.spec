# Scenario 40: Unauthenticated Nick Takeover & Out of Order Registration
# Tests state transitions when NICK/USER are sent before PASS vs another client registering
CLIENTS C1, C2

# C1 sends NICK without PASS
C1 SEND NICK Ali002
# C1 is not registered yet, sending JOIN fails with 451
C1 SEND JOIN #room06
C1 EXPECT 451 * :You have not registered

# C2 connects with valid credentials
C2 SEND PASS 1234
C2 SEND NICK Bob002
C2 SEND USER bob002 0 * :Bob002
C2 EXPECT 001 Bob002 :*

# C1 completes registration with PASS and USER
C1 SEND PASS 1234
C1 SEND USER ali002 0 * :Ali002
C1 EXPECT 001 Ali002 :*

# Now C1 can join channels
C1 SEND JOIN #room06
C1 EXPECT :Ali002!* JOIN #room06
