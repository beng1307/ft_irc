# 37_JOIN_missing_params_error.spec
# Tests that sending JOIN with empty or missing parameters returns 461 ERR_NEEDMOREPARAMS
# Expected: Server returns 461 Alice JOIN :Not enough parameters.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali120
C1 SEND USER ali120 0 * :Ali120
C1 EXPECT 001 Ali120 :*

# Send bare JOIN with no arguments
C1 SEND JOIN
C1 EXPECT 461 Ali120 JOIN :Not enough parameters

# Send invalid channel prefix (e.g. not starting with # or &)
C1 SEND JOIN invalidchannel
C1 EXPECT 403 Ali120 invalidchannel :No such channel
