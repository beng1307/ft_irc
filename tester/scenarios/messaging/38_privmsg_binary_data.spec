# PRIVMSG with binary/null bytes in message.
# Tests robustness of message parsing and transmission.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Send message with embedded binary data (CTCP-like but not full CTCP)
C1 SEND_RAW PRIVMSG Bob :\x01ACTION performs an action\x01\r\n

# Server should not crash; message should be handled somehow
C2 EXPECT_CONNECTED
C1 EXPECT_CONNECTED

# Verify clients remain responsive
C1 SEND PING :alive
C1 EXPECT PONG * :alive
