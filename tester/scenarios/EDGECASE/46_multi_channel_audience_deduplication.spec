# Scenario 46: Multi-Channel Audience Deduplication
# Tests that a user sharing multiple mutual channels receives exactly one NICK change notification
CLIENTS C1, C2

# Register Alice and Bob
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Both join #chanA, #chanB, and #chanC
C1 SEND JOIN #chanA
C1 EXPECT :Alice!* JOIN #chanA
C2 SEND JOIN #chanA
C2 WAIT_RECV :Bob!* JOIN #chanA

C1 SEND JOIN #chanB
C1 EXPECT :Alice!* JOIN #chanB
C2 SEND JOIN #chanB
C2 WAIT_RECV :Bob!* JOIN #chanB

C1 SEND JOIN #chanC
C1 EXPECT :Alice!* JOIN #chanC
C2 SEND JOIN #chanC
C2 WAIT_RECV :Bob!* JOIN #chanC

# Alice changes nick to Alicia
C1 SEND NICK Alicia
C1 EXPECT :Alice!* NICK :Alicia

# Bob receives the NICK change notification
C2 WAIT_RECV :Alice!* NICK :Alicia

# Assert Bob has no extra duplicate NICK broadcasts in queue
C2 EXPECT_NONE 200ms
