# 02_NICK_unregistered_collision.spec
# Tests out-of-order registration where C1 sends NICK before PASS, and C2 claims the same nick.
# Expected: Since C1 has not sent PASS yet, C1 does not reserve the nick. C2 successfully registers.
# When C1 later completes PASS+USER, C1 gets 433 Nickname is already in use.
CLIENTS C1, C2

# C1 sends NICK first (before PASS)
C1 SEND NICK Cha184

# C2 connects and claims 'Charlie02'
C2 SEND PASS 1234
C2 SEND NICK Cha184
C2 SEND USER u184 0 * :Cha184 02
C2 EXPECT 001 Cha184 :*

# C1 completes registration with PASS and USER, but Charlie02 is now taken
C1 SEND PASS 1234
C1 SEND USER u184 0 * :Usr184 01
C1 EXPECT 433 * Cha184 :Nickname is already in use


