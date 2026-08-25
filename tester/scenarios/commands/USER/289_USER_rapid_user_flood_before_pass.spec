# 289_USER_rapid_user_flood_before_pass.spec
# Stress / State Stability: Rapid unauthenticated USER command flood before PASS
CLIENTS C1

C1 SEND USER u1 0 * :Real 1
C1 SEND USER u2 0 * :Real 2
C1 SEND USER u3 0 * :Real 3
C1 SEND USER u4 0 * :Real 4
C1 SEND USER u5 0 * :Real 5
C1 SEND USER finaluser 0 * :Final Realname
C1 SEND PASS 1234
C1 SEND NICK FloodNick
C1 EXPECT 001 FloodNick :*
C1 EXPECT 002 FloodNick :*
C1 EXPECT 003 FloodNick :*
C1 EXPECT 004 FloodNick *
C1 EXPECT_CONNECTED
