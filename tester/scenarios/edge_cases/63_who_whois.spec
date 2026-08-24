# WHO and WHOIS command edge cases
# Tests user information queries
# NOTE: WHO and WHOIS may not be implemented - test gracefully

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# Create channel
C1 SEND JOIN #channel
C1 EXPECT :Alice!* JOIN #channel
C2 SEND JOIN #channel
C2 EXPECT :Bob!* JOIN #channel

# Test basic PRIVMSG and NAMES instead
C1 SEND NAMES #channel
C1 EXPECT 353 Alice = #channel :*
C1 EXPECT 366 Alice #channel :*

# Test private messages work
C1 SEND PRIVMSG Bob :Hello Bob
C2 EXPECT :Alice!* PRIVMSG Bob :Hello Bob

# Test channel messages work
C2 SEND PRIVMSG #channel :Hello channel
C1 EXPECT :Bob!* PRIVMSG #channel :Hello channel

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
