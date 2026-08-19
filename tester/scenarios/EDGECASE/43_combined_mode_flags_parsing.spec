# Scenario 43: Combined Mode Flags Parsing
# Tests multi-character mode changes with mixed parameters (+itk-l+o secret Bob)
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates #complexmodes and sets limit first
C1 SEND JOIN #complexmodes
C1 EXPECT :Alice!* JOIN #complexmodes
C1 SEND MODE #complexmodes +l 10
C1 EXPECT :Alice!* MODE #complexmodes +l 10

# Bob joins
C2 SEND JOIN #complexmodes
C2 WAIT_RECV :Bob!* JOIN #complexmodes

# Alice executes combined mode change: +i (invite), +t (topic), +k (key), -l (clear limit), +o (op Bob)
C1 SEND MODE #complexmodes +itk-l+o secretkey Bob
C1 EXPECT :Alice!* MODE #complexmodes +itk-l+o secretkey Bob
C2 WAIT_RECV :Alice!* MODE #complexmodes +itk-l+o secretkey Bob

# Query current modes
C1 SEND MODE #complexmodes
C1 EXPECT 324 Alice #complexmodes +itk secretkey

# Bob (now operator) can set topic under +t
C2 SEND TOPIC #complexmodes :Bob Is Now Op
C2 EXPECT :Bob!* TOPIC #complexmodes :Bob Is Now Op
C1 WAIT_RECV :Bob!* TOPIC #complexmodes :Bob Is Now Op
