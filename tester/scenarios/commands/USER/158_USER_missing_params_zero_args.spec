# 158_USER_missing_params_zero_args.spec
# Tests ERR_NEEDMOREPARAMS (461) when USER is sent with 0 parameters or only whitespace
CLIENTS C1

C1 SEND USER
C1 EXPECT 461 * USER :Not enough parameters

C1 SEND USER   
C1 EXPECT 461 * USER :Not enough parameters
