# 151_PART_rapid_double_part_solo.spec
# Tests behavior when a solo user in a channel sends PART #chan twice in rapid succession.
# 1st PART destroys the channel. 2nd PART fails with 403 ERR_NOSUCHCHANNEL.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*
C1 SEND JOIN #solo
C1 EXPECT :Alice!* JOIN #solo

# First PART: succeeds and destroys #solo
C1 SEND PART #solo :Bye
C1 EXPECT :Alice!* PART #solo :Bye

# Second PART: channel does not exist anymore -> 403
C1 SEND PART #solo :Bye
C1 EXPECT 403 Alice #solo :No such channel
