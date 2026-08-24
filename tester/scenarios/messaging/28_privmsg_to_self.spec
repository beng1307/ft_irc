# PRIVMSG from client to itself.
# Server should either allow it or provide graceful error handling.

CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Client sends PRIVMSG to itself
C1 SEND PRIVMSG Alice :Talking to myself

# Either message is received or rejected gracefully without crash
C1 EXPECT_CONNECTED

# Verify client is still responsive
C1 SEND PING :alive
C1 EXPECT PONG * :alive
