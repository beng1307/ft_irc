# 65_MODE_multi_target_operator_pipeline_error_isolation.spec
# Adversarial / Edge Case: Multi-operator change where one target is valid and one is non-existent (e.g. MODE #chan +oo Bob GhostUser).
# Expected: Server promotes Bob, reports 401 for GhostUser, and isolates failures cleanly.
CLIENTS C1, C2

# C1 is Alice65
C1 SEND PASS 1234
C1 SEND NICK Ali182
C1 SEND USER ali182 0 * :Ali182
C1 EXPECT 001 Ali182 :*

# C2 is Bob65
C2 SEND PASS 1234
C2 SEND NICK Bob182
C2 SEND USER bob182 0 * :Bob182
C2 EXPECT 001 Bob182 :*

C1 SEND JOIN #isolation65
C1 EXPECT 353 Ali182 = #isolation65 :@Ali182
C1 EXPECT 366 Ali182 #isolation65 :End of /NAMES list

C2 SEND JOIN #isolation65
C1 WAIT_RECV :Bob182!* JOIN #isolation65

# Alice sends +oo with 1 valid user and 1 invalid user
C1 SEND MODE #isolation65 +oo Bob182 GhostUser
C1 EXPECT 401 Ali182 GhostUser :No such nick/channel
# Bob must still have been promoted
C1 EXPECT :Ali182!* MODE #isolation65 +o Bob182
