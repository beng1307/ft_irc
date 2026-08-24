# 11_CAP_case_insensitivity.spec
# Tests RFC/IRC standard case-insensitivity on CAP subcommands (e.g. 'CAP ls').
# Expected: Server replies with ':localhost CAP * LS :' (or equivalent CAP LS reply).
# Bug: Server does case-sensitive 'arguments[0] == "LS"', silently dropping 'CAP ls'.
CLIENTS C1

C1 SEND CAP ls
C1 EXPECT :localhost CAP * LS :
