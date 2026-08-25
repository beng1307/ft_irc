# 67_INVITE_trailing_tokens_ignored.spec
# Tests INVITE command with surplus trailing parameters.
# Expected: Server processes target and channel, ignoring extra arguments.
CLIENTS C1, C2

# Alice registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Alice67
C1 SEND USER alice67 0 * :Alice
C1 EXPECT 001 Alice67 :*
C1 SEND JOIN #extraparams67
C1 EXPECT :Alice67!* JOIN #extraparams67

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob67
C2 SEND USER bob67 0 * :Bob
C2 EXPECT 001 Bob67 :*

# Alice sends INVITE with extra trailing parameters
C1 SEND INVITE Bob67 #extraparams67 extra tokens here
C1 EXPECT 341 Alice67 Bob67 #extraparams67
C2 WAIT_RECV :Alice67!alice67@localhost INVITE Bob67 :#extraparams67
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
