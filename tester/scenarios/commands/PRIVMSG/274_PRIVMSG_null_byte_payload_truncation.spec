# 274_PRIVMSG_null_byte_payload_truncation.spec
# Malicious Actor: Embedded NULL byte (\0) inside message payload
# Expected: Server handles binary NULL safely without buffer over-read, crash, or hanging.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali306
C1 SEND USER ali306 0 * :Ali306
C1 EXPECT 001 Ali306 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob306
C2 SEND USER bob306 0 * :Bob306
C2 EXPECT 001 Bob306 :*

# C1 sends message with embedded \0 byte
C1 SEND PRIVMSG Bob306 :hello\0world
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
