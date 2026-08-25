# 57_MODE_target_nonexistent_user_operator_attempt.spec
# Edge Case: Operator attempts to promote/demote a completely non-existent nickname.
# Expected: Server returns 401 ERR_NOSUCHNICK without altering channel state.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #targettest
C1 EXPECT 353 Alice = #targettest :@Alice
C1 EXPECT 366 Alice #targettest :End of /NAMES list

# Alice targets ghost/non-existent users
C1 SEND MODE #targettest +o NonExistentUser
C1 EXPECT 401 Alice NonExistentUser :No such nick/channel

C1 SEND MODE #targettest -o NonExistentUser
C1 EXPECT 401 Alice NonExistentUser :No such nick/channel

# Verify channel still has only Alice as operator
C1 SEND MODE #targettest
C1 EXPECT 324 Alice #targettest +
