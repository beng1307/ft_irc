# 273_PRIVMSG_tab_delimiter_rejection.spec
# Edge Case: Using ASCII Tab (\t) instead of standard space as command delimiter
# Expected: Server either parses tab as whitespace or rejects with 421 Unknown command.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 uses tab delimiter
C1 SEND PRIVMSG\tBob\t:Tab test
C1 EXPECT 421 Alice Unknown command.
C2 NO_RECV :Alice!* PRIVMSG Bob :Tab test
