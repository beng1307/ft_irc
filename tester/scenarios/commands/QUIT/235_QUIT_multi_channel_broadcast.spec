# 208_QUIT_multi_channel_broadcast.spec
# Tests that QUIT audience is deduplicated: peers sharing multiple channels receive QUIT exactly once; non-shared peers receive 0.
CLIENTS C1, C2, C3, C4

# Ali235 (C1)
C1 SEND PASS 1234
C1 SEND NICK Ali235
C1 SEND USER ali235 0 * :Ali235
C1 EXPECT 001 Ali235 :*

# Bob235 (C2)
C2 SEND PASS 1234
C2 SEND NICK Bob323
C2 SEND USER bob323 0 * :Bob323
C2 EXPECT 001 Bob323 :*

# Cha235 (C3)
C3 SEND PASS 1234
C3 SEND NICK Cha235
C3 SEND USER cha235 0 * :Cha235
C3 EXPECT 001 Cha235 :*

# Dav235 (C4)
C4 SEND PASS 1234
C4 SEND NICK Dav235
C4 SEND USER dav235 0 * :Dav235
C4 EXPECT 001 Dav235 :*

# Setup channel topology:
# #chan1: Ali235, Bob235
# #chan2: Ali235, Bob235
# #chan3: Ali235, Cha235
# #isolated: Dav235
C1 SEND JOIN #chan1
C1 EXPECT :Ali235!* JOIN #chan1
C2 SEND JOIN #chan1
C2 WAIT_RECV :Bob323!* JOIN #chan1
C1 WAIT_RECV :Bob323!* JOIN #chan1

C1 SEND JOIN #chan2
C1 EXPECT :Ali235!* JOIN #chan2
C2 SEND JOIN #chan2
C2 WAIT_RECV :Bob323!* JOIN #chan2
C1 WAIT_RECV :Bob323!* JOIN #chan2

C1 SEND JOIN #chan3
C1 EXPECT :Ali235!* JOIN #chan3
C3 SEND JOIN #chan3
C3 WAIT_RECV :Cha235!* JOIN #chan3
C1 WAIT_RECV :Cha235!* JOIN #chan3

C4 SEND JOIN #isolated
C4 EXPECT :Dav235!* JOIN #isolated

# Ali235 quits
C1 SEND QUIT :Multi-channel exit
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob235 (shares #chan1 and #chan2) must receive QUIT exactly once
C2 WAIT_RECV :Ali235!* QUIT :Multi-channel exit

# Cha235 (shares #chan3) receives QUIT
C3 WAIT_RECV :Ali235!* QUIT :Multi-channel exit

# Dav235 is unaffected and can message normally
C4 SEND PRIVMSG #isolated :Still running
C4 EXPECT_CONNECTED
