# 285_USER_nick_collision_race_with_user_state.spec
# Multi-Client State Desynchronization / Collision Race
# C1 sets USER user_c1, PASS 1234, but its NICK collides with registered C2.
# C1 then picks a unique NICK. Verifies C1's username state was preserved and registers correctly.
CLIENTS C1, C2

# C2 registers fully as TargetNick
C2 SEND PASS 1234
C2 SEND NICK TargetNick
C2 SEND USER user_c2 0 * :C2
C2 EXPECT 001 TargetNick :*
C2 SEND JOIN #shared
C2 EXPECT 353 TargetNick = #shared :@TargetNick

# C1 buffers USER and PASS, then collides on NICK
C1 SEND USER user_c1 0 * :C1
C1 SEND PASS 1234
C1 SEND NICK TargetNick
C1 EXPECT 433 * TargetNick :Nickname is already in use

# C1 recovers with a unique nickname
C1 SEND NICK UniqueNick
C1 EXPECT 001 UniqueNick :*

# C1 joins #shared; C2 must see C1 with user_c1
C1 SEND JOIN #shared
C2 EXPECT :UniqueNick!user_c1@localhost JOIN #shared
