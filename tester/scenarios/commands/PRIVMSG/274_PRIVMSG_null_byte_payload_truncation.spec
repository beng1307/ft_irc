# 274_PRIVMSG_null_byte_payload_truncation.spec
# Malicious Actor: Embedded NULL byte (\0) inside message payload
# Expected: Server handles binary NULL safely without buffer over-read, crash, or hanging.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 sends message with embedded \0 byte
C1 SEND PRIVMSG Bob :hello\0world
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
