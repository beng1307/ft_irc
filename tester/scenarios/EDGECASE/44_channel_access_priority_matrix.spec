# Scenario 44: Channel Access Priority Matrix
# Tests sequential rejection evaluation order on channels configured with +i, +k, and +l
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali006
C1 SEND USER ali006 0 * :Ali006
C1 EXPECT 001 Ali006 :*

C2 SEND PASS 1234
C2 SEND NICK Bob006
C2 SEND USER bob006 0 * :Bob006
C2 EXPECT 001 Bob006 :*

# Alice creates #triplestack and sets +i, +k pass, +l 1 (full)
C1 SEND JOIN #triplestack
C1 EXPECT :Ali006!* JOIN #triplestack
C1 SEND MODE #triplestack +i
C1 EXPECT :Ali006!* MODE #triplestack +i
C1 SEND MODE #triplestack +k keypass
C1 EXPECT :Ali006!* MODE #triplestack +k keypass
C1 SEND MODE #triplestack +l 1
C1 EXPECT :Ali006!* MODE #triplestack +l 1

# Bob tries to join with wrong key -> +i checked first (473)
C2 SEND JOIN #triplestack wrongkey
C2 EXPECT 473 Bob006 #triplestack :Cannot join channel (+i)

# Alice invites Bob
C1 SEND INVITE Bob006 #triplestack
C1 EXPECT 341 Ali006 Bob006 #triplestack
C2 WAIT_RECV :Ali006!* INVITE Bob006 :#triplestack

# Bob is invited, now tries to join with wrong key -> +k checked second (475)
C2 SEND JOIN #triplestack wrongkey
C2 EXPECT 475 Bob006 #triplestack :Cannot join channel (+k)

# Bob is invited, provides correct key -> +l checked third (471)
C2 SEND JOIN #triplestack keypass
C2 EXPECT 471 Bob006 #triplestack :Cannot join channel (+l)

# Alice raises user limit to 2
C1 SEND MODE #triplestack +l 2
C1 EXPECT :Ali006!* MODE #triplestack +l 2

# Now Bob joins successfully
C2 SEND JOIN #triplestack keypass
C2 WAIT_RECV :Bob006!* JOIN #triplestack
C1 WAIT_RECV :Bob006!* JOIN #triplestack
