# MODE with mismatched parameters and flags.
# +k requires parameter but +i doesn't - test parser robustness.

CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali059
C1 SEND USER ali059 0 * :Ali059
C1 EXPECT 001 Ali059 :*

C1 SEND JOIN #paramchannel
C1 EXPECT :Ali059!* JOIN #paramchannel

# +ik: +i doesn't need param, +k does
# Send: +ik key1 key2
# Parser should: apply +i (no param needed), +k (uses key1), ignore key2
C1 SEND MODE #paramchannel +ik key1 key2
C1 EXPECT_CONNECTED

# Query to see what was actually applied
C1 SEND MODE #paramchannel
C1 EXPECT 324 Ali059 #paramchannel *

# Clear and test again
C1 SEND MODE #paramchannel -i
C1 SEND MODE #paramchannel -k

# +kl: both need params
# Send: +kl key1 5
# Should work
C1 SEND MODE #paramchannel +kl key1 5
C1 EXPECT :Ali059!* MODE #paramchannel +kl key1 5

# +kl: both need params
# Send: +kl key1
# Missing parameter - should error
C1 SEND MODE #paramchannel +kl key1
C1 EXPECT 461 Ali059 MODE :Not enough parameters

# Verify mode didn't partially apply
C1 SEND MODE #paramchannel
C1 EXPECT 324 Ali059 #paramchannel +kl *

C1 EXPECT_CONNECTED
