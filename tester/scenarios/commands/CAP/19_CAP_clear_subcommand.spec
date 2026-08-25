# 19_CAP_clear_subcommand.spec
# Tests CAP CLEAR subcommand to reset negotiated capabilities.
# Expected: Server acknowledges with CAP * ACK :.
# Bug: Server drops CAP CLEAR silently.
CLIENTS C1

C1 SEND CAP CLEAR
C1 EXPECT :localhost CAP * ACK :
