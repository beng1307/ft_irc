# 101_KICK_excess_trailing_parameters.spec
# Tests handling of excess trailing arguments injected between target nickname and colon comment (KICK #lobby101K Bob extra1 extra2 :Real comment).
# Expected: Server kicks Bob and broadcasts the comment 'Real comment' cleanly without protocol desynchronization.
CLIENTS C1, C2

# Alice registers and creates #lobby101K
C1 SEND PASS 1234
C1 SEND NICK Ali122
C1 SEND USER ali122 0 * :Ali122
C1 EXPECT 001 Ali122 :*
C1 SEND JOIN #lobby101K
C1 EXPECT :Ali122!* JOIN #lobby101K

# Bob registers and joins #lobby101K
C2 SEND PASS 1234
C2 SEND NICK Bob122
C2 SEND USER bob122 0 * :Bob122
C2 EXPECT 001 Bob122 :*
C2 SEND JOIN #lobby101K
C2 EXPECT :Bob122!* JOIN #lobby101K
C1 WAIT_RECV :Bob122!* JOIN #lobby101K

# Alice sends KICK with extra parameters; KICK uses positional 3rd argument as comment (:extra1)
C1 SEND KICK #lobby101K Bob122 extra1 extra2 :Real comment
C1 EXPECT :Ali122!* KICK #lobby101K Bob122 :extra1
C2 EXPECT :Ali122!* KICK #lobby101K Bob122 :extra1

