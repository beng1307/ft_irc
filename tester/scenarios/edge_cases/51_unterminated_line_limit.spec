# Reject oversized, unterminated IRC input without impacting other clients.
CLIENTS C1, C2

# C1 exceeds the RFC 512-byte IRC message limit before it sends CRLF.
C1 REPEAT_RAW 511 A
C1 EXPECT_DISCONNECT

# C2 confirms the event loop remains responsive after the abusive client drops.
C2 SEND PING :still-alive
C2 EXPECT PONG * :still-alive
C2 EXPECT_CONNECTED