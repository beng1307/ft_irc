# 199_PASS_missing_params_zero_args.spec
# RFC 1459/2812 Requirement: PASS without parameters must return ERR_NEEDMOREPARAMS (461)
CLIENTS C1

C1 SEND PASS
C1 EXPECT 461 * PASS :Not enough parameters
