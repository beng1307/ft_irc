# 70_INVITE_mode_toggle_persistence.spec
# Tests that an invitation persists across channel mode toggles (+i -> -i -> +i).
# Expected: Client invited during initial +i state can join after +i is removed and subsequently re-enabled.
CLIENTS C1, C2

# Alice creates channel and sets +i
C1 SEND PASS 1234
C1 SEND NICK Alice68
C1 SEND USER alice68 0 * :Alice
C1 EXPECT 001 Alice68 :*
C1 SEND JOIN #persistchan68
C1 EXPECT :Alice68!* JOIN #persistchan68
C1 SEND MODE #persistchan68 +i
C1 EXPECT :Alice68!* MODE #persistchan68 +i

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob68
C2 SEND USER bob68 0 * :Bob
C2 EXPECT 001 Bob68 :*

# Alice invites Bob
C1 SEND INVITE Bob68 #persistchan68
C1 EXPECT 341 Alice68 Bob68 #persistchan68
C2 WAIT_RECV :Alice68!alice68@localhost INVITE Bob68 :#persistchan68

# Alice removes +i, then re-adds +i
C1 SEND MODE #persistchan68 -i
C1 EXPECT :Alice68!* MODE #persistchan68 -i
C1 SEND MODE #persistchan68 +i
C1 EXPECT :Alice68!* MODE #persistchan68 +i

# Bob joins using the persistent invitation
C2 SEND JOIN #persistchan68
C2 WAIT_RECV :Bob68!* JOIN #persistchan68
C1 WAIT_RECV :Bob68!* JOIN #persistchan68
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
