# 169_USER_colon_prefix_username.spec
# Tests colon-prefixed username argument (e.g. USER :alice 0 * :Alice Smith)
# Expected: Leading colon on first parameter is stripped or handled as username 'alice'.
# Bug: split_arguments captures ':alice 0 * :Alice Smith' as single argument with spaces,
# corrupting the prefix mask to ':Alice!alice 0 * :Alice Smith@localhost'
CLIENTS C1, C2

C2 SEND PASS 1234
C2 SEND NICK Bob391
C2 SEND USER bob391 0 * :Bob391
C2 EXPECT 001 Bob391 :*
C2 SEND JOIN #testchan
C2 EXPECT 353 Bob391 = #testchan :@Bob391

C1 SEND PASS 1234
C1 SEND NICK Ali391
C1 SEND USER :ali391 0 * :Ali391 Smith
C1 EXPECT 001 Ali391 :*

C1 SEND JOIN #testchan
C2 EXPECT :Ali391!ali391@localhost JOIN #testchan
