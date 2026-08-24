# MODE with mismatched parameters and flags.
# +k requires parameter but +i doesn't - test parser robustness.

CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #paramchannel
C1 EXPECT :Alice!* JOIN #paramchannel

# +ik: +i doesn't need param, +k does
# Send: +ik key1 key2
# Parser should: apply +i (no param needed), +k (uses key1), ignore key2
C1 SEND MODE #paramchannel +ik key1 key2
C1 EXPECT_CONNECTED

# Query to see what was actually applied
C1 SEND MODE #paramchannel
C1 EXPECT 324 Alice #paramchannel *

# Clear and test again
C1 SEND MODE #paramchannel -i
C1 SEND MODE #paramchannel -k

# +kl: both need params
# Send: +kl key1 5
# Should work
C1 SEND MODE #paramchannel +kl key1 5
C1 EXPECT :Alice!* MODE #paramchannel +kl key1 5

# +kl: both need params
# Send: +kl key1
# Missing parameter - should error
C1 SEND MODE #paramchannel +kl key1
C1 EXPECT 461 Alice MODE :Not enough parameters

# Verify mode didn't partially apply
C1 SEND MODE #paramchannel
C1 EXPECT 324 Alice #paramchannel +kl *

C1 EXPECT_CONNECTED
