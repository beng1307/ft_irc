# 116_TOPIC_multi_word_without_colon.spec
# Tests TOPIC with multiple parameters without leading colon (e.g. TOPIC #chan word1 word2)
# Expected: Server processes parameters and updates topic or rejects invalid syntax.
# Bug: Server treats entire command as TOPIC query 'TOPIC #chan' because line does not contain ' :', ignoring extra parameters.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali344
C1 SEND USER ali344 0 * :Ali344
C1 EXPECT 001 Ali344 :*
C1 SEND JOIN #testchan
C1 EXPECT :Ali344!* JOIN #testchan

# Alice sends topic without colon
C1 SEND TOPIC #testchan WordOne WordTwo
C1 EXPECT :Ali344!* TOPIC #testchan :*
