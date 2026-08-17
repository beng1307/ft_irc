# Tests invalid nickname characters (432), dynamic nickname changes with broadcast, and in-use collisions (433).
CLIENTS C1, C2

# AUTH-07: Erroneous Nickname testing during registration
C1 SEND PASS 1234
C1 SEND NICK "123 digit"
C1 EXPECT 432 * :*
C1 SEND NICK #channelnick
C1 EXPECT 432 * :*
C1 SEND NICK AliceValid
C1 SEND USER alice 0 * :Alice Valid
C1 EXPECT 001 AliceValid :*

# Register C2
C2 SEND PASS 1234
C2 SEND NICK BobValid
C2 SEND USER bob 0 * :Bob Valid
C2 EXPECT 001 BobValid :*

# Join shared channel to test broadcast propagation
C1 SEND JOIN #rename
C1 EXPECT :AliceValid!* JOIN #rename
C2 SEND JOIN #rename
C2 WAIT_RECV :BobValid!* JOIN #rename
C1 WAIT_RECV :BobValid!* JOIN #rename

# AUTH-10: C1 attempts dynamic rename to C2's active nick -> 433 ERR_NICKNAMEINUSE
C1 SEND NICK BobValid
C1 EXPECT 433 AliceValid BobValid :*

# AUTH-09: C1 performs valid dynamic rename -> broadcasts :AliceValid!* NICK :AliceNew
C1 SEND NICK AliceNew
C1 EXPECT :AliceValid!* NICK :AliceNew
C2 WAIT_RECV :AliceValid!* NICK :AliceNew

# Verify subsequent messaging uses the updated nickname
C2 SEND PRIVMSG AliceNew :Hey renamed Alice
C1 WAIT_RECV :BobValid!* PRIVMSG AliceNew :Hey renamed Alice
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
