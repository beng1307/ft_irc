# 08_NICK_dynamic_broadcast_audience.spec
# Tests NICK change broadcasting:
# 1. Self receives :old!user@host NICK :new
# 2. Mutual channel members receive exactly one NICK broadcast even if sharing multiple channels
# 3. Non-mutual clients receive nothing
CLIENTS C1, C2, C3

# C1 registers as Alice08
C1 SEND PASS 1234
C1 SEND NICK Alice08
C1 SEND USER user08 0 * :Alice 08
C1 EXPECT 001 Alice08 :*

# C2 registers as Bob08
C2 SEND PASS 1234
C2 SEND NICK Bob08
C2 SEND USER user08 0 * :Bob 08
C2 EXPECT 001 Bob08 :*

# C3 registers as Charlie08
C3 SEND PASS 1234
C3 SEND NICK Charlie08
C3 SEND USER user08 0 * :Charlie 08
C3 EXPECT 001 Charlie08 :*

# C1 and C2 join #chan1_08 and #chan2_08
C1 SEND JOIN #chan1_08
C2 SEND JOIN #chan1_08
C1 WAIT_RECV :Bob08!* JOIN #chan1_08

C1 SEND JOIN #chan2_08
C2 SEND JOIN #chan2_08
C1 WAIT_RECV :Bob08!* JOIN #chan2_08

# C3 joins an unrelated channel #chan3_08
C3 SEND JOIN #chan3_08

# C1 changes nickname to Alicia08
C1 SEND NICK Alicia08
C1 WAIT_RECV :Alice08!* NICK :Alicia08
C2 WAIT_RECV :Alice08!* NICK :Alicia08

# C2 should NOT receive duplicate NICK broadcast despite sharing 2 channels
C2 EXPECT_NONE 200ms

# C3 is not in mutual channels and must receive nothing
C3 EXPECT_NONE 200ms
