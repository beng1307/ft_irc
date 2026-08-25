# 57_MODE_target_nonexistent_user_operator_attempt.spec
# Edge Case: Operator attempts to promote/demote a completely non-existent nickname.
# Expected: Server returns 401 ERR_NOSUCHNICK without altering channel state.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali174
C1 SEND USER ali174 0 * :Ali174
C1 EXPECT 001 Ali174 :*

C1 SEND JOIN #targettest
C1 EXPECT 353 Ali174 = #targettest :@Ali174
C1 EXPECT 366 Ali174 #targettest :End of /NAMES list

# Alice targets ghost/non-existent users
C1 SEND MODE #targettest +o NonExistentUser
C1 EXPECT 401 Ali174 NonExistentUser :No such nick/channel

C1 SEND MODE #targettest -o NonExistentUser
C1 EXPECT 401 Ali174 NonExistentUser :No such nick/channel

# Verify channel still has only Alice as operator
C1 SEND MODE #targettest
C1 EXPECT 324 Ali174 #targettest +
