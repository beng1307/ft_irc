# 02_NICK_unregistered_collision.spec
# Tests out-of-order registration where C1 sends NICK before PASS, and C2 tries to claim the same nick.
# Expected: C2 receives 433 Nickname is already in use (or C2 is blocked from dual-registering as Charlie).
# Bug: C1 has pass_ok=false and registered=false, so C2's collision check is bypassed. Both C1 and C2 register as Charlie.
CLIENTS C1, C2

# C1 sends NICK first (before PASS)
C1 SEND NICK Charlie

# C2 connects and attempts to claim the same nickname 'Charlie'
C2 SEND PASS 1234
C2 SEND NICK Charlie
C2 EXPECT 433 * Charlie :Nickname is already in use # CHANGE TO EXPECT SUCCESS!! FOR US.

# C1 completes registration with PASS and USER
C1 SEND PASS 1234
C1 SEND USER charlie 0 * :Charlie
C1 EXPECT 001 Charlie :*
