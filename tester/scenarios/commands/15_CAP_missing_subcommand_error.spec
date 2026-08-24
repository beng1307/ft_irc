# 15_CAP_missing_subcommand_error.spec
# Tests bare CAP command with zero arguments.
# Expected: Server replies with 461 ERR_NEEDMOREPARAMS.
# Bug: Server silently ignores CAP without arguments and sends no error reply.
CLIENTS C1

C1 SEND CAP
C1 EXPECT :localhost 461 * :*
