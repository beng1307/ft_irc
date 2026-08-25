# 182_PING_whitespace_only.spec
# Tests PING with trailing whitespace only (no actual origin token)
# RFC Expectation: Returns ERR_NOORIGIN (409)
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali268
C1 SEND USER ali268 0 * :Ali268 Smith
C1 EXPECT 001 Ali268 :*

C1 SEND PING   
C1 EXPECT 409 Ali268 :No origin specified
