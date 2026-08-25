# Scenario 43: Combined Mode Flags Parsing
# Tests multi-character mode changes with mixed parameters (+itk-l+o secret Bob)
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali005
C1 SEND USER ali005 0 * :Ali005
C1 EXPECT 001 Ali005 :*

C2 SEND PASS 1234
C2 SEND NICK Bob005
C2 SEND USER bob005 0 * :Bob005
C2 EXPECT 001 Bob005 :*

# Alice creates #complexmodes and sets limit first
C1 SEND JOIN #complexmodes
C1 EXPECT :Ali005!* JOIN #complexmodes
C1 SEND MODE #complexmodes +l 10
C1 EXPECT :Ali005!* MODE #complexmodes +l 10

# Bob joins
C2 SEND JOIN #complexmodes
C2 WAIT_RECV :Bob005!* JOIN #complexmodes

# Alice executes combined mode change: +i (invite), +t (topic), +k (key), -l (clear limit), +o (op Bob)
C1 SEND MODE #complexmodes +itk-l+o secretkey Bob005
C1 EXPECT :Ali005!* MODE #complexmodes +itk-l+o secretkey Bob005
C2 WAIT_RECV :Ali005!* MODE #complexmodes +itk-l+o secretkey Bob005

# Query current modes
C1 SEND MODE #complexmodes
C1 EXPECT 324 Ali005 #complexmodes +itk secretkey

# Bob (now operator) can set topic under +t
C2 SEND TOPIC #complexmodes :Bob005 Is Now Op
C2 EXPECT :Bob005!* TOPIC #complexmodes :Bob005 Is Now Op
C1 WAIT_RECV :Bob005!* TOPIC #complexmodes :Bob005 Is Now Op
