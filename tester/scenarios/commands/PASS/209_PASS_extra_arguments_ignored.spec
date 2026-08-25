# 209_PASS_extra_arguments_ignored.spec
# Extra arguments after password should be ignored per IRC spec and registration should proceed
CLIENTS C1

C1 SEND PASS 1234 extra_token1 extra_token2
C1 SEND NICK PAlice209
C1 SEND USER ali237 0 * :Ali237 Smith
C1 EXPECT 001 PAlice209 :*
