# 159_USER_missing_params_one_arg.spec
# Tests RFC 1459/2812 4-parameter requirement on USER (USER <user> <mode> <unused> :<realname>)
# Expected: Server sends 461 USER :Not enough parameters when only 1 argument is provided.
# Bug: Server checks if (arguments.empty()) and accepts 1 argument, registering the client prematurely.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali381
C1 SEND USER ali381
C1 EXPECT 461 Ali381 USER :Not enough parameters
