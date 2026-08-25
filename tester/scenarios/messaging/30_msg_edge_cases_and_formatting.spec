# Tests PRIVMSG missing text (412) and preservation of complex spacing and colons in message payloads.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali435
C1 SEND USER ali435 0 * :Ali435
C1 EXPECT 001 Ali435 :*

C2 SEND PASS 1234
C2 SEND NICK Bob435
C2 SEND USER bob435 0 * :Bob435
C2 EXPECT 001 Bob435 :*

C1 SEND JOIN #msgformat
C1 EXPECT :Ali435!* JOIN #msgformat
C2 SEND JOIN #msgformat
C2 WAIT_RECV :Bob435!* JOIN #msgformat
C1 WAIT_RECV :Bob435!* JOIN #msgformat

# MSG-05: PRIVMSG missing text parameter
C1 SEND PRIVMSG Bob435
C1 EXPECT 412 Ali435 :*

C1 SEND PRIVMSG #msgformat
C1 EXPECT 412 Ali435 :*

# MSG-08: Complex trailing parameter with multiple leading and inner colons and spaces
C1 SEND PRIVMSG #msgformat ::hello :world:   extra   spaces:
C2 WAIT_RECV :Ali435!* PRIVMSG #msgformat ::hello :world:   extra   spaces:

C2 SEND PRIVMSG Ali435 ::direct :msg :with :colons
C1 WAIT_RECV :Bob435!* PRIVMSG Ali435 ::direct :msg :with :colons

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
