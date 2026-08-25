# 103_KICK_special_char_nickname.spec
# Tests KICK command on target with special characters in nickname (e.g. _Bob_).
# Expected: Server correctly locates _Bob_ and executes KICK.
CLIENTS C1, C2

# Alice registers and creates #lobby103K
C1 SEND PASS 1234
C1 SEND NICK Ali124
C1 SEND USER ali124 0 * :Ali124
C1 EXPECT 001 Ali124 :*
C1 SEND JOIN #lobby103K
C1 EXPECT :Ali124!* JOIN #lobby103K

# Target registers as _Bob_ and joins #lobby103K
C2 SEND PASS 1234
C2 SEND NICK _Bob_
C2 SEND USER bob124 0 * :Bob124
C2 EXPECT 001 _Bob_ :*
C2 SEND JOIN #lobby103K
C2 EXPECT :_Bob_!* JOIN #lobby103K
C1 WAIT_RECV :_Bob_!* JOIN #lobby103K

# Alice kicks _Bob_
C1 SEND KICK #lobby103K _Bob_ :Underscore nick test
C1 EXPECT :Ali124!* KICK #lobby103K _Bob_ :Underscore nick test
C2 EXPECT :Ali124!* KICK #lobby103K _Bob_ :Underscore nick test
