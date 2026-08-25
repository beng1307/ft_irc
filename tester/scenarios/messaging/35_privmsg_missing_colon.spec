# PRIVMSG missing colon separator.
# "PRIVMSG Bob hello" instead of "PRIVMSG Bob :hello"
# Server should either handle gracefully or reject with proper error.

CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali440
C1 SEND USER ali440 0 * :Ali440
C1 EXPECT 001 Ali440 :*

# Missing colon - some parsers treat this as multi-word message
# Others reject it. Test for stability.
C1 SEND_RAW PRIVMSG Bob440 hello\r\n

# Server should remain responsive after malformed command
C1 EXPECT_CONNECTED
C1 SEND PING :alive
C1 EXPECT PONG * :alive
