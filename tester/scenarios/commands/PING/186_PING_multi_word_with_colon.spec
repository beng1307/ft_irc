# 186_PING_multi_word_with_colon.spec
# Tests trailing colon payload containing multiple words separated by spaces
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING :hello world foo bar
C1 EXPECT :localhost PONG localhost :hello world foo bar
