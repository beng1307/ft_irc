# 273_PRIVMSG_tab_delimiter_rejection.spec
# Edge Case: Using ASCII Tab (\t) instead of standard space as command delimiter
# Expected: Server either parses tab as whitespace or rejects with 421 Unknown command.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali305
C1 SEND USER ali305 0 * :Ali305
C1 EXPECT 001 Ali305 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob305
C2 SEND USER bob305 0 * :Bob305
C2 EXPECT 001 Bob305 :*

# C1 uses tab delimiter
C1 SEND PRIVMSG\tBob\t:Tab test
C1 EXPECT 421 Ali305 Unknown command.
C2 NO_RECV :Ali305!* PRIVMSG Bob305 :Tab test
