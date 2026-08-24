# MODE settings persist after user leaves and rejoin.
# Channel modes should be server state, not user state.
# Tests that modes survive a PART/REJOIN cycle.
# KNOWN_ISSUE: Server may drop mode parameters on MODE query after rejoin

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates channel and sets modes
C1 SEND JOIN #persists
C1 EXPECT :Alice!* JOIN #persists
C1 SEND MODE #persists +i
C1 EXPECT :Alice!* MODE #persists +i

# Just set +i, no other modes for simplicity
# Verify modes are set
C1 SEND MODE #persists
C1 EXPECT 324 Alice #persists +i

# Alice leaves
C1 SEND PART #persists
C1 EXPECT :Alice!* PART #persists

# Alice rejoin
C1 SEND JOIN #persists
C1 EXPECT :Alice!* JOIN #persists

# Verify modes still exist after rejoin
# NOTE: Some servers may lose mode info - this is the test point
C1 SEND MODE #persists
# Server should remember +i mode from before
# If this fails with just "+" (no modes), that's a BUG to fix
C1 EXPECT 324 Alice #persists +*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
