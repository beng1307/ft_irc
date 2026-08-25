# Tests pre-registration command rejection (451), permuted registration, duplicate registration errors (462), and IRCv3 CAP negotiation.
CLIENTS C1, C2

# AUTH-05: Attempt commands before registration -> 451 ERR_NOTREGISTERED
C1 SEND JOIN #test
C1 EXPECT 451 * :*
C1 SEND PRIVMSG Bob453 :Hello
C1 EXPECT 451 * :*
C1 SEND MODE #test +i
C1 EXPECT 451 * :*
C1 SEND TOPIC #test :New topic
C1 EXPECT 451 * :*

# AUTH-13 & AUTH-02: IRCv3 CAP handshake + Permuted PASS -> USER -> NICK sequence
C1 SEND CAP LS
C1 EXPECT :* CAP * LS :*
C1 SEND PASS 1234
C1 SEND USER ali453 0 * :Ali453 Permuted
C1 EXPECT_NONE 150ms
C1 SEND NICK AlicePerm
C1 SEND CAP END
C1 EXPECT 001 AlicePerm :*

# AUTH-04 & AUTH-12: Duplicate registration attempts -> 462 ERR_ALREADYREGISTRED
C1 SEND PASS 1234
C1 EXPECT 462 AlicePerm :*
C1 SEND USER ali453 0 * :Ali453 Again
C1 EXPECT 462 AlicePerm :*
C1 EXPECT_CONNECTED

# Register C2 standardly to ensure server state is intact
C2 SEND PASS 1234
C2 SEND NICK BobStd
C2 SEND USER bob453 0 * :Bob453 Standard
C2 EXPECT 001 BobStd :*
C2 EXPECT_CONNECTED
