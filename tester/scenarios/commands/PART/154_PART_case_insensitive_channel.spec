# 154_PART_case_insensitive_channel.spec
# Tests RFC 2812 case-insensitivity when parting: JOIN #test then PART #TEST
# Expected: Server treats #test and #TEST as identical and parts client.
# Bug: Server map lookup is case-sensitive, returning 403 ERR_NOSUCHCHANNEL for #TEST.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali223
C1 SEND USER ali223 0 * :Ali223
C1 EXPECT 001 Ali223 :*

# Join lowercase #test
C1 SEND JOIN #test
C1 EXPECT :Ali223!* JOIN #test

# Part uppercase #TEST
C1 SEND PART #TEST :Leaving
C1 EXPECT :Ali223!* PART #test :Leaving
