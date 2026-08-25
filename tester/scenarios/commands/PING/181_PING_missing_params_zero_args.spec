# 181_PING_missing_params_zero_args.spec
# RFC 1459/2812 Requirement: PING without parameters must return ERR_NOORIGIN (409)
# Flaw: Server currently accepts 0 args and replies with ':localhost PONG localhost :localhost'
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING
C1 EXPECT 409 Alice :No origin specified
