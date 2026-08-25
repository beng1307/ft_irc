# 162_USER_already_registered_rejection.spec
# Tests ERR_ALREADYREGISTRED (462) when USER is issued after client is fully registered
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Wonderland
C1 EXPECT 001 Alice :*

# Attempt to re-issue USER command
C1 SEND USER bob 0 * :Bob Builder
C1 EXPECT 462 Alice :You may not reregister
