# 02_NICK_unregistered_collision.spec
# Tests out-of-order registration where C1 sends NICK before PASS, and C2 tries to claim the same nick.
<<<<<<< Updated upstream:tester/unsupported/02_NICK_unregistered_collision.spec
# Expected: C1's unregistered nickname reservation does not block C2 from using Charlie.
=======
# Expected: C2 receives 433 Nickname is already in use (or C2 is blocked from dual-registering as NickCharlie02).
# Bug: C1 has pass_ok=false and registered=false, so C2's collision check is bypassed. Both C1 and C2 register as NickCharlie02.
>>>>>>> Stashed changes:tester/scenarios/commands/NICK/02_NICK_unregistered_collision.spec
CLIENTS C1, C2

# C1 sends NICK first (before PASS)
C1 SEND NICK NickCharlie02

# C2 connects and attempts to claim the same nickname 'NickCharlie02'
C2 SEND PASS 1234
<<<<<<< Updated upstream:tester/unsupported/02_NICK_unregistered_collision.spec
C2 SEND NICK Charlie
C2 EXPECT SUCCESS
=======
C2 SEND NICK NickCharlie02
C2 EXPECT 433 * NickCharlie02 :Nickname is already in use
>>>>>>> Stashed changes:tester/scenarios/commands/NICK/02_NICK_unregistered_collision.spec

# C1 completes registration with PASS and USER
C1 SEND PASS 1234
C1 SEND USER user02 0 * :Charlie 02
C1 EXPECT 001 NickCharlie02 :*
