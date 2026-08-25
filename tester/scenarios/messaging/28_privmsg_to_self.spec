# PRIVMSG from client to itself.
# Server should either allow it or provide graceful error handling.

CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali433
C1 SEND USER ali433 0 * :Ali433
C1 EXPECT 001 Ali433 :*

# Client sends PRIVMSG to itself
C1 SEND PRIVMSG Ali433 :Talking to myself

# Either message is received or rejected gracefully without crash
C1 EXPECT_CONNECTED

# Verify client is still responsive
C1 SEND PING :alive
C1 EXPECT PONG * :alive
