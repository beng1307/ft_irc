# 69_INVITE_trailing_tokens_ignored.spec
# Tests INVITE command with surplus trailing parameters.
# Expected: Server processes target and channel, ignoring extra arguments.
CLIENTS C1, C2

# Alice registers and creates channel
C1 SEND PASS 1234
C1 SEND NICK Ali094
C1 SEND USER ali094 0 * :Ali094
C1 EXPECT 001 Ali094 :*
C1 SEND JOIN #extraparams67
C1 EXPECT :Ali094!* JOIN #extraparams67

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob094
C2 SEND USER bob094 0 * :Bob094
C2 EXPECT 001 Bob094 :*

# Alice sends INVITE with extra trailing parameters
C1 SEND INVITE Bob094 #extraparams67 extra tokens here
C1 EXPECT 341 Ali094 Bob094 #extraparams67
C2 WAIT_RECV :Ali094!ali094@localhost INVITE Bob094 :#extraparams67
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
