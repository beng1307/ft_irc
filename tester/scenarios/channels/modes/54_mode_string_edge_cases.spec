# Scenario 54: Mode String Edge Cases (Expected Correct Behavior)
# This test asserts correct, standard IRC behavior on mode edge cases.
# Current server bugs/bad behaviors should cause this test to FAIL.

CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali064
C1 SEND USER ali064 0 * :Ali064
C1 EXPECT 001 Ali064 :*

C2 SEND PASS 1234
C2 SEND NICK Bob064
C2 SEND USER bob064 0 * :Bob064
C2 EXPECT 001 Bob064 :*

# Alice creates #testmode and Bob joins
C1 SEND JOIN #testmode
C1 EXPECT :Ali064!* JOIN #testmode
C2 SEND JOIN #testmode
C2 WAIT_RECV :Bob064!* JOIN #testmode
C1 WAIT_RECV :Bob064!* JOIN #testmode

# 1. Unknown mode without leading sign should return 472 ERR_UNKNOWNMODE, not be silently ignored
C1 SEND MODE #testmode x
C1 EXPECT 472 Ali064 x :*

# 2. Ban query with standard '+b' syntax should return 368 RPL_ENDOFBANLIST, not 472 unknown mode
C1 SEND MODE #testmode +b
C1 EXPECT 368 Ali064 #testmode :*

# 3. Duplicate mode flags '+ii' should normalize to '+i' in broadcast
C1 SEND MODE #testmode +ii
C1 EXPECT :Ali064!* MODE #testmode +i
C2 WAIT_RECV :Ali064!* MODE #testmode +i

# 4. Self-cancelling mode changes '+t-t' produce no net change and should not broadcast
C1 SEND MODE #testmode +t-t
C1 EXPECT_NONE 0.5
C1 SEND MODE #testmode
C1 EXPECT 324 Ali064 #testmode +i

# 5. Parameter starvation in compound modes (+ko Bob):
# When not enough parameters are given for all flags, it should fail with 461 and NOT apply +k with a stolen nick
C1 SEND MODE #testmode +ko Bob064
C1 EXPECT 461 Ali064 MODE :*
C1 SEND MODE #testmode
C1 EXPECT 324 Ali064 #testmode +i

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
