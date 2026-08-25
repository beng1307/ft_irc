# 56_INVITE_nonexistent_target_nick.spec
# Tests INVITE issued targeting a non-existent nickname.
# Expected: Server rejects with 401 ERR_NOSUCHNICK.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali081
C1 SEND USER ali081 0 * :Ali081
C1 EXPECT 001 Ali081 :*

C1 SEND JOIN #testchan54
C1 EXPECT :Ali081!* JOIN #testchan54

# Alice54 invites non-existent user Ghost
C1 SEND INVITE Ghost #testchan54
C1 EXPECT 401 Ali081 Ghost :No such nick/channel
C1 EXPECT_CONNECTED
