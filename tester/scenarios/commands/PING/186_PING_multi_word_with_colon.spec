# 186_PING_multi_word_with_colon.spec
# Tests trailing colon payload containing multiple words separated by spaces
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali272
C1 SEND USER ali272 0 * :Ali272 Smith
C1 EXPECT 001 Ali272 :*

C1 SEND PING :hello world foo bar
C1 EXPECT :localhost PONG localhost :hello world foo bar
