# 17_CAP_colon_prefix_subcommand.spec
# Tests colon-prefixed subcommand syntax (CAP :LS).
# Expected: Server strips the leading colon and processes the subcommand as LS.
# Bug: Server checks arguments[0] == "LS", failing on ":LS" and dropping the command.
CLIENTS C1

C1 SEND CAP :LS
C1 EXPECT :localhost CAP * LS :

#TODO: Behaviour maybe has to be changed on parser. Not directly on CAP.
