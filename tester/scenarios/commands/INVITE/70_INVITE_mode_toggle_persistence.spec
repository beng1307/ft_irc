# 70_INVITE_mode_toggle_persistence.spec
# Tests that an invitation persists across channel mode toggles (+i -> -i -> +i).
# Expected: Client invited during initial +i state can join after +i is removed and subsequently re-enabled.
CLIENTS C1, C2

# Alice creates channel and sets +i
C1 SEND PASS 1234
C1 SEND NICK Ali095
C1 SEND USER ali095 0 * :Ali095
C1 EXPECT 001 Ali095 :*
C1 SEND JOIN #persistchan68
C1 EXPECT :Ali095!* JOIN #persistchan68
C1 SEND MODE #persistchan68 +i
C1 EXPECT :Ali095!* MODE #persistchan68 +i

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob095
C2 SEND USER bob095 0 * :Bob095
C2 EXPECT 001 Bob095 :*

# Alice invites Bob
C1 SEND INVITE Bob095 #persistchan68
C1 EXPECT 341 Ali095 Bob095 #persistchan68
C2 WAIT_RECV :Ali095!ali095@localhost INVITE Bob095 :#persistchan68

# Alice removes +i, then re-adds +i
C1 SEND MODE #persistchan68 -i
C1 EXPECT :Ali095!* MODE #persistchan68 -i
C1 SEND MODE #persistchan68 +i
C1 EXPECT :Ali095!* MODE #persistchan68 +i

# Bob joins using the persistent invitation
C2 SEND JOIN #persistchan68
C2 WAIT_RECV :Bob095!* JOIN #persistchan68
C1 WAIT_RECV :Bob095!* JOIN #persistchan68
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
