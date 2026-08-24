# 08_NICK_dynamic_broadcast_audience.spec
# Tests NICK change broadcasting:
# 1. Self receives :old!user@host NICK :new
# 2. Mutual channel members receive exactly one NICK broadcast even if sharing multiple channels
# 3. Non-mutual clients receive nothing
CLIENTS C1, C2, C3

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C3 registers as Charlie
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# C1 and C2 join #chan1 and #chan2
C1 SEND JOIN #chan1
C2 SEND JOIN #chan1
C1 WAIT_RECV :Bob!* JOIN #chan1

C1 SEND JOIN #chan2
C2 SEND JOIN #chan2
C1 WAIT_RECV :Bob!* JOIN #chan2

# C3 joins an unrelated channel #chan3
C3 SEND JOIN #chan3

# C1 changes nickname to Alicia
C1 SEND NICK Alicia
C1 WAIT_RECV :Alice!* NICK :Alicia
C2 WAIT_RECV :Alice!* NICK :Alicia

# C2 should NOT receive duplicate NICK broadcast despite sharing 2 channels
C2 EXPECT_NONE 200ms

# C3 is not in mutual channels and must receive nothing
C3 EXPECT_NONE 200ms
