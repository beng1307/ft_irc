# 154_PART_case_insensitive_channel.spec
# Tests RFC 2812 case-insensitivity when parting: JOIN #test then PART #TEST
# Expected: Server treats #test and #TEST as identical and parts client.
# Bug: Server map lookup is case-sensitive, returning 403 ERR_NOSUCHCHANNEL for #TEST.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Join lowercase #test
C1 SEND JOIN #test
C1 EXPECT :Alice!* JOIN #test

# Part uppercase #TEST
C1 SEND PART #TEST :Leaving
C1 EXPECT :Alice!* PART #test :Leaving
