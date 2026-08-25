# 65_MODE_multi_target_operator_pipeline_error_isolation.spec
# Adversarial / Edge Case: Multi-operator change where one target is valid and one is non-existent (e.g. MODE #chan +oo Bob GhostUser).
# Expected: Server promotes Bob, reports 401 for GhostUser, and isolates failures cleanly.
CLIENTS C1, C2

# C1 is Alice65
C1 SEND PASS 1234
C1 SEND NICK Alice65
C1 SEND USER alice65 0 * :Alice65
C1 EXPECT 001 Alice65 :*

# C2 is Bob65
C2 SEND PASS 1234
C2 SEND NICK Bob65
C2 SEND USER bob65 0 * :Bob65
C2 EXPECT 001 Bob65 :*

C1 SEND JOIN #isolation65
C1 EXPECT 353 Alice65 = #isolation65 :@Alice65
C1 EXPECT 366 Alice65 #isolation65 :End of /NAMES list

C2 SEND JOIN #isolation65
C1 WAIT_RECV :Bob65!* JOIN #isolation65

# Alice sends +oo with 1 valid user and 1 invalid user
C1 SEND MODE #isolation65 +oo Bob65 GhostUser
C1 EXPECT 401 Alice65 GhostUser :No such nick/channel
# Bob must still have been promoted
C1 EXPECT :Alice65!* MODE #isolation65 +o Bob65
