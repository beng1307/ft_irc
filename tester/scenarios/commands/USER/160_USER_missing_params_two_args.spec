# 160_USER_missing_params_two_args.spec
# Tests RFC 1459/2812 4-parameter requirement on USER
# Expected: Server sends 461 USER :Not enough parameters when only 2 arguments are provided.
# Bug: Server accepts 2 arguments and registers the client.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0
C1 EXPECT 461 Alice USER :Not enough parameters
