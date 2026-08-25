# 16_CAP_invalid_subcommand_error.spec
# Tests unrecognized CAP subcommand (e.g. CAP BOGUS).
# Expected: Server replies with 410 ERR_INVALIDCAPCMD or 421 ERR_UNKNOWNCOMMAND.
# Bug: Server silently drops unknown subcommands without any error numeric.
CLIENTS C1

C1 SEND CAP BOGUS
C1 EXPECT :localhost 410 * :*
