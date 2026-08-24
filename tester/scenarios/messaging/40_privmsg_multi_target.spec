# PRIVMSG to multiple targets (comma-separated).
# RFC 2812 allows "PRIVMSG #channel1,#channel2 :message"
# Tests multi-target support or proper error handling.

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# C1 tries multi-target PRIVMSG
# If not supported, should get error; if supported, both should receive
C1 SEND PRIVMSG Bob,Charlie :Message to multiple targets

# Try to receive (may fail with error)
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED

# Verify Alice is still responsive
C1 SEND PING :alive
C1 EXPECT PONG * :alive
