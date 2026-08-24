# PRIVMSG with trailing spaces in target nickname/channel.
# Edge case: "PRIVMSG Alice " (space before colon) should work or error gracefully.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# PRIVMSG with trailing space in target
# This tests parser robustness
C1 SEND PRIVMSG Bob  :Message with trailing space in target
C2 WAIT_RECV :Alice!* PRIVMSG Bob :Message with trailing space in target

# Multiple spaces in target should still work
C1 SEND PRIVMSG Bob    :Multiple spaces
C2 WAIT_RECV :Alice!* PRIVMSG Bob :Multiple spaces

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
