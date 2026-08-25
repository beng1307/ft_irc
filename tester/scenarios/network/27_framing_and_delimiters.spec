# Validates CRLF termination, whitespace tolerance, 512-byte buffers, and mid-stream disconnect handling.
# Design Decision:
# 1. Bare \n without \r: Delimiting strictly on \r\n (standard IRC RFC 1459/2812). Bare \n is not accepted as delimiter.
# 2. Leading whitespace: IRC BNF command grammar does not allow leading spaces before command; treated as unknown/malformed command (421).
# 3. Empty lines (\r\n\r\n): Empty lines are completely ignored per RFC 2812 §2.3 and do not send any response.
CLIENTS C1, C2

# NET-05: Empty lines (\r\n\r\n) are ignored (no reply sent)
C1 SEND_RAW \r\n\r\n
C1 EXPECT_NONE 100ms

# Leading whitespace triggers 421 Unknown command
C1 SEND_RAW    PASS   1234   \r\n
C1 EXPECT * 421 *

# Send valid registration commands
C1 SEND PASS 1234
C1 SEND NICK AliceLF
C1 SEND USER ali446 0 * :Ali446 LF
C1 EXPECT 001 AliceLF :*

# NET-06: 512-byte boundary resilience (send long 550-byte PRIVMSG payload without crashing server)
C1 SEND_RAW PRIVMSG AliceLF :AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\r\n
C1 EXPECT_CONNECTED

# NET-09: Client C2 sends half a command and disconnects abruptly (RST)
C2 SEND_RAW NICK PartialNic
C2 RESET
C2 EXPECT_DISCONNECT

# Verify C1 is unharmed and C2 can reconnect and register cleanly
C1 EXPECT_CONNECTED
C2 RECONNECT
C2 SEND PASS 1234
C2 SEND NICK BobNet
C2 SEND USER bob446 0 * :Bob446 Net
C2 EXPECT 001 BobNet :*
C2 EXPECT_CONNECTED
