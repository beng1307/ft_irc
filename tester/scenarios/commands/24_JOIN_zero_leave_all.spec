# 24_JOIN_zero_leave_all.spec
# Tests RFC 2812 §3.2.1 special command 'JOIN 0' to part all joined channels
# Expected: Server parts the client from all currently joined channels with PART broadcasts.
# Bug: Server rejects '0' with 403 0 :No such channel because '0' does not start with '#' or '&'.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 and C2 join #roomA and #roomB
C1 SEND JOIN #roomA
C2 SEND JOIN #roomA
C1 WAIT_RECV :Bob!* JOIN #roomA

C1 SEND JOIN #roomB
C2 SEND JOIN #roomB
C1 WAIT_RECV :Bob!* JOIN #roomB

# C1 sends 'JOIN 0' to leave all channels
C1 SEND JOIN 0

# C2 should receive PART broadcasts from Alice for both channels
C2 WAIT_RECV :Alice!* PART #roomA*
C2 WAIT_RECV :Alice!* PART #roomB*
