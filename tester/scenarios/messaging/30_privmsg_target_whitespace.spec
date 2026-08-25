# PRIVMSG with trailing spaces in target nickname/channel.
# Edge case: "PRIVMSG Alice " (space before colon) should work or error gracefully.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali436
C1 SEND USER ali436 0 * :Ali436
C1 EXPECT 001 Ali436 :*

C2 SEND PASS 1234
C2 SEND NICK Bob436
C2 SEND USER bob436 0 * :Bob436
C2 EXPECT 001 Bob436 :*

# PRIVMSG with trailing space in target
# This tests parser robustness
C1 SEND PRIVMSG Bob436  :Message with trailing space in target
C2 WAIT_RECV :Ali436!* PRIVMSG Bob436 :Message with trailing space in target

# Multiple spaces in target should still work
C1 SEND PRIVMSG Bob436    :Multiple spaces
C2 WAIT_RECV :Ali436!* PRIVMSG Bob436 :Multiple spaces

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
