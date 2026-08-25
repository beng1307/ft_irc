# 209_PASS_extra_arguments_ignored.spec
# Extra arguments after password should be ignored per IRC spec and registration should proceed
CLIENTS C1

C1 SEND PASS 1234 extra_token1 extra_token2
C1 SEND NICK PassAlice209
C1 SEND USER alice209 0 * :Alice Smith
C1 EXPECT 001 PassAlice209 :*
