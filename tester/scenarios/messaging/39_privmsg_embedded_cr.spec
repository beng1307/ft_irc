# PRIVMSG with CR in message (but no LF).
# Edge case: embedded carriage return that's not a line terminator.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Message with embedded CR (but inside content, not terminator)
# This is a stress test for line parsing
C1 SEND_RAW PRIVMSG Bob :Hello\rWorld\r\n

# Either message arrives or connection stays stable
C2 EXPECT_CONNECTED
C1 EXPECT_CONNECTED
