# PRIVMSG with message close to IRC line limit (~490 chars, just under 512).
# Server should accept this and deliver the message.
# Beyond 512 total bytes, server may disconnect (RFC 2812 compliance).

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Send message with ~470 character payload
# (Total line will be just under 512 bytes: "PRIVMSG Bob :" + 470 chars + CRLF)
C1 SEND PRIVMSG Bob :aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

# Message should be delivered successfully
C2 WAIT_RECV :Alice!* PRIVMSG Bob :aaaaaaaaaa*
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED

# Verify both clients are still responsive after near-limit message
C1 SEND PING :test1
C1 EXPECT PONG * :test1
C2 SEND PING :test2
C2 EXPECT PONG * :test2
