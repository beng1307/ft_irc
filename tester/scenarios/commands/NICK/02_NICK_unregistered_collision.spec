# 02_NICK_unregistered_collision.spec
# Tests out-of-order registration where C1 sends NICK before PASS, and C2 claims the same nick.
# Expected: Since C1 has not sent PASS yet, C1 does not reserve the nick. C2 successfully registers.
# When C1 later completes PASS+USER, C1 gets 433 Nickname is already in use.
CLIENTS C1, C2

# C1 sends NICK first (before PASS)
C1 SEND NICK Charlie02

# C2 connects and claims 'Charlie02'
C2 SEND PASS 1234
C2 SEND NICK Charlie02
C2 SEND USER user02 0 * :Charlie 02
C2 EXPECT 001 Charlie02 :*

# C1 completes registration with PASS and USER, but Charlie02 is now taken
C1 SEND PASS 1234
C1 SEND USER user01 0 * :User 01
C1 EXPECT 433 * Charlie02 :Nickname is already in use


