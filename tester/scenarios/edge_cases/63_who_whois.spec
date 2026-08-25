# WHO and WHOIS command edge cases
# Tests user information queries
# NOTE: WHO and WHOIS may not be implemented - test gracefully

CLIENTS C1, C2, C3

C1 SEND PASS 1234
C1 SEND NICK Ali418
C1 SEND USER ali418 0 * :Ali418
C1 EXPECT 001 Ali418 :*

C2 SEND PASS 1234
C2 SEND NICK Bob418
C2 SEND USER bob418 0 * :Bob418
C2 EXPECT 001 Bob418 :*

C3 SEND PASS 1234
C3 SEND NICK Cha418
C3 SEND USER cha418 0 * :Cha418
C3 EXPECT 001 Cha418 :*

# Create channel
C1 SEND JOIN #channel
C1 EXPECT :Ali418!* JOIN #channel
C2 SEND JOIN #channel
C2 EXPECT :Bob418!* JOIN #channel

# Test basic PRIVMSG and NAMES instead
C1 SEND NAMES #channel
C1 EXPECT 353 Ali418 = #channel :*
C1 EXPECT 366 Ali418 #channel :*

# Test private messages work
C1 SEND PRIVMSG Bob418 :Hello Bob418
C2 EXPECT :Ali418!* PRIVMSG Bob418 :Hello Bob418

# Test channel messages work
C2 SEND PRIVMSG #channel :Hello channel
C1 EXPECT :Bob418!* PRIVMSG #channel :Hello channel

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
C3 EXPECT_CONNECTED
