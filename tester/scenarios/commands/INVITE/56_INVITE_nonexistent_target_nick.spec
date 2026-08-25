# 56_INVITE_nonexistent_target_nick.spec
# Tests INVITE issued targeting a non-existent nickname.
# Expected: Server rejects with 401 ERR_NOSUCHNICK.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice54
C1 SEND USER alice54 0 * :Alice
C1 EXPECT 001 Alice54 :*

C1 SEND JOIN #testchan54
C1 EXPECT :Alice54!* JOIN #testchan54

# Alice54 invites non-existent user Ghost
C1 SEND INVITE Ghost #testchan54
C1 EXPECT 401 Alice54 Ghost :No such nick/channel
C1 EXPECT_CONNECTED
