# 02_NICK_unregistered_collision.spec
# Tests out-of-order registration where C1 sends NICK before PASS, and C2 tries to claim the same nick.
# Expected: C1's unregistered nickname reservation does not block C2 from using Charlie.
CLIENTS C1, C2

# C1 sends NICK first (before PASS)
C1 SEND NICK Charlie

# C2 connects and attempts to claim the same nickname 'Charlie'
C2 SEND PASS 1234
C2 SEND NICK Charlie
C2 EXPECT SUCCESS

# C1 completes registration with PASS and USER
C1 SEND PASS 1234
C1 SEND USER charlie 0 * :Charlie
C1 EXPECT 001 Charlie :*
