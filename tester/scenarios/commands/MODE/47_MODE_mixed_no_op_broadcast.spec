# 47_MODE_mixed_no_op_broadcast.spec
# Tests mode change broadcast when some flags are no-ops and only other flags change state (e.g. MODE #chan +i+t when +i is already active)
# Expected: Server broadcasts only the flags that actually changed state (:Alice!* MODE #chan +t).
# Bug: append_mode_change blindly includes +i, broadcasting misleading ":Alice!* MODE #chan +it".
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali164
C1 SEND USER ali164 0 * :Ali164
C1 EXPECT 001 Ali164 :*

C2 SEND PASS 1234
C2 SEND NICK Bob164
C2 SEND USER bob164 0 * :Bob164
C2 EXPECT 001 Bob164 :*

C1 SEND JOIN #chan
C1 EXPECT 353 Ali164 = #chan :@Ali164
C1 EXPECT 366 Ali164 #chan :End of /NAMES list

C2 SEND JOIN #chan
C1 WAIT_RECV :Bob164!* JOIN #chan

# Set initial mode +i
C1 SEND MODE #chan +i
C1 EXPECT :Ali164!* MODE #chan +i
C2 EXPECT :Ali164!* MODE #chan +i

# Send +i+t where +i is no-op and +t is new
C1 SEND MODE #chan +i+t
# Must only broadcast changed flag +t
C1 EXPECT :Ali164!* MODE #chan +t
C2 EXPECT :Ali164!* MODE #chan +t
