# 103_KICK_special_char_nickname.spec
# Tests KICK command on target with special characters in nickname (e.g. _Bob_).
# Expected: Server correctly locates _Bob_ and executes KICK.
CLIENTS C1, C2

# Alice registers and creates #lobby
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #lobby
C1 EXPECT :Alice!* JOIN #lobby

# Target registers as _Bob_ and joins #lobby
C2 SEND PASS 1234
C2 SEND NICK _Bob_
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 _Bob_ :*
C2 SEND JOIN #lobby
C2 EXPECT :_Bob_!* JOIN #lobby
C1 WAIT_RECV :_Bob_!* JOIN #lobby

# Alice kicks _Bob_
C1 SEND KICK #lobby _Bob_ :Underscore nick test
C1 EXPECT :Alice!* KICK #lobby _Bob_ :Underscore nick test
C2 EXPECT :Alice!* KICK #lobby _Bob_ :Underscore nick test
