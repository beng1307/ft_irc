# 18_CAP_list_subcommand.spec
# Tests CAP LIST subcommand querying currently enabled capabilities.
# Expected: Server replies with ':localhost CAP * LIST :' (empty active capabilities).
# Bug: Server has no branch for LIST and drops the query silently.
CLIENTS C1

C1 SEND CAP LIST
C1 EXPECT :localhost CAP * LIST :
