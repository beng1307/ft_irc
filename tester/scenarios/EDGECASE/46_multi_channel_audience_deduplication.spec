# Scenario 46: Multi-Channel Audience Deduplication
# Tests that a user sharing multiple mutual channels receives exactly one NICK change notification
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Ali008
C1 SEND USER ali008 0 * :Ali008
C1 EXPECT 001 Ali008 :*

C2 SEND PASS 1234
C2 SEND NICK Bob008
C2 SEND USER bob008 0 * :Bob008
C2 EXPECT 001 Bob008 :*

# Both join #chanA, #chanB, and #chanC
C1 SEND JOIN #chanA
C1 EXPECT :Ali008!* JOIN #chanA
C2 SEND JOIN #chanA
C2 WAIT_RECV :Bob008!* JOIN #chanA

C1 SEND JOIN #chanB
C1 EXPECT :Ali008!* JOIN #chanB
C2 SEND JOIN #chanB
C2 WAIT_RECV :Bob008!* JOIN #chanB

C1 SEND JOIN #chanC
C1 EXPECT :Ali008!* JOIN #chanC
C2 SEND JOIN #chanC
C2 WAIT_RECV :Bob008!* JOIN #chanC

# Alice changes nick to Alicia
C1 SEND NICK Ali008
C1 EXPECT :Ali008!* NICK :Ali008

# Bob receives the NICK change notification
C2 WAIT_RECV :Ali008!* NICK :Ali008

# Assert Bob has no extra duplicate NICK broadcasts in queue
C2 EXPECT_NONE 200ms
