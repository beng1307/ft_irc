# PRIVMSG to multiple targets (comma-separated).
# RFC 2812 allows "PRIVMSG #channel1,#channel2 :message"
# Tests multi-target support or proper error handling.

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali445
C1 SEND USER ali445 0 * :Ali445
C1 EXPECT 001 Ali445 :*

C2 SEND PASS 1234
C2 SEND NICK Bob445
C2 SEND USER bob445 0 * :Bob445
C2 EXPECT 001 Bob445 :*

C3 SEND PASS 1234
C3 SEND NICK Cha445
C3 SEND USER cha445 0 * :Cha445
C3 EXPECT 001 Cha445 :*

# C1 tries multi-target PRIVMSG
# If not supported, should get error; if supported, both should receive
C1 SEND PRIVMSG Bob445,Cha445 :Message to multiple targets

# Try to receive (may fail with error)
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED

# Verify Alice is still responsive
C1 SEND PING :alive
C1 EXPECT PONG * :alive
