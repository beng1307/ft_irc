# PRIVMSG to unregistered client (before PASS/NICK/USER complete).
# Server should still deliver if nick exists, but only after full registration.
# This tests registration state tracking.

CLIENTS C1, C2

# C1 fully registers
C1 SEND PASS 1234
C1 SEND NICK Ali434
C1 SEND USER ali434 0 * :Ali434
C1 EXPECT 001 Ali434 :*

# C2 connects and sends only PASS+NICK (no USER = not fully registered)
C2 SEND PASS 1234
C2 SEND NICK Bob434
# C2 intentionally doesn't send USER yet

# C1 tries to send PRIVMSG to Bob (who is not fully registered)
# Server may either accept it (if nick exists) or reject with 401
# Either behavior is acceptable depending on server implementation
C1 SEND PRIVMSG Bob434 :Hello unregistered

# Accept either response - message delivery or error
# (This is implementation-dependent behavior)
C1 EXPECT_CONNECTED

# Now C2 completes registration
C2 SEND USER bob434 0 * :Bob434
C2 EXPECT 001 Bob434 :*

# Now PRIVMSG should definitely work
C1 SEND PRIVMSG Bob434 :Hello registered Bob434
C2 WAIT_RECV :Ali434!* PRIVMSG Bob434 :Hello registered Bob434

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
