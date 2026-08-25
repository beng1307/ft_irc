# 162_USER_already_registered_rejection.spec
# Tests ERR_ALREADYREGISTRED (462) when USER is issued after client is fully registered
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali384
C1 SEND USER ali384 0 * :Ali384 Wonderland
C1 EXPECT 001 Ali384 :*

# Attempt to re-issue USER command
C1 SEND USER bob384 0 * :Bob384 Builder
C1 EXPECT 462 Ali384 :You may not reregister
