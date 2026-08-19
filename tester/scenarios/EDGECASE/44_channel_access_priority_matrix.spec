# Scenario 44: Channel Access Priority Matrix
# Tests sequential rejection evaluation order on channels configured with +i, +k, and +l
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates #triplestack and sets +i, +k pass, +l 1 (full)
C1 SEND JOIN #triplestack
C1 EXPECT :Alice!* JOIN #triplestack
C1 SEND MODE #triplestack +i
C1 EXPECT :Alice!* MODE #triplestack +i
C1 SEND MODE #triplestack +k keypass
C1 EXPECT :Alice!* MODE #triplestack +k keypass
C1 SEND MODE #triplestack +l 1
C1 EXPECT :Alice!* MODE #triplestack +l 1

# Bob tries to join with wrong key -> +i checked first (473)
C2 SEND JOIN #triplestack wrongkey
C2 EXPECT 473 Bob #triplestack :Cannot join channel (+i)

# Alice invites Bob
C1 SEND INVITE Bob #triplestack
C1 EXPECT 341 Alice Bob #triplestack
C2 WAIT_RECV :Alice!* INVITE Bob :#triplestack

# Bob is invited, now tries to join with wrong key -> +k checked second (475)
C2 SEND JOIN #triplestack wrongkey
C2 EXPECT 475 Bob #triplestack :Cannot join channel (+k)

# Bob is invited, provides correct key -> +l checked third (471)
C2 SEND JOIN #triplestack keypass
C2 EXPECT 471 Bob #triplestack :Cannot join channel (+l)

# Alice raises user limit to 2
C1 SEND MODE #triplestack +l 2
C1 EXPECT :Alice!* MODE #triplestack +l 2

# Now Bob joins successfully
C2 SEND JOIN #triplestack keypass
C2 WAIT_RECV :Bob!* JOIN #triplestack
C1 WAIT_RECV :Bob!* JOIN #triplestack
