# Tests PRIVMSG missing text (412) and preservation of complex spacing and colons in message payloads.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #msgformat
C1 EXPECT :Alice!* JOIN #msgformat
C2 SEND JOIN #msgformat
C2 WAIT_RECV :Bob!* JOIN #msgformat
C1 WAIT_RECV :Bob!* JOIN #msgformat

# MSG-05: PRIVMSG missing text parameter
C1 SEND PRIVMSG Bob
C1 EXPECT 412 Alice :*

C1 SEND PRIVMSG #msgformat
C1 EXPECT 412 Alice :*

# MSG-08: Complex trailing parameter with multiple leading and inner colons and spaces
C1 SEND PRIVMSG #msgformat ::hello :world:   extra   spaces:
C2 WAIT_RECV :Alice!* PRIVMSG #msgformat ::hello :world:   extra   spaces:

C2 SEND PRIVMSG Alice ::direct :msg :with :colons
C1 WAIT_RECV :Bob!* PRIVMSG Alice ::direct :msg :with :colons

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
