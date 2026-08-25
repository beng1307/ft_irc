CLIENTS C1

# Authenticate and register C1
C1 SEND PASS 1234
C1 SEND NICK Ali419
C1 SEND USER ali419 0 * :Ali419
C1 EXPECT 001 * :*

# Join channel
C1 SEND JOIN #chan
C1 EXPECT :Ali419!* JOIN #chan

# Send binary control characters (e.g. CTCP / control bytes \x01\x02)
C1 SEND_RAW \x01\x02PRIVMSG #chan :hello\r\n

# Assert server doesn't crash and remains connected and responsive
C1 EXPECT_CONNECTED
C1 SEND PING :alive
C1 EXPECT PONG * :alive
