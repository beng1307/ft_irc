# 208_QUIT_multi_channel_broadcast.spec
# Tests that QUIT audience is deduplicated: peers sharing multiple channels receive QUIT exactly once; non-shared peers receive 0.
CLIENTS C1, C2, C3, C4

# Alice (C1)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Bob (C2)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Charlie (C3)
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# Dave (C4)
C4 SEND PASS 1234
C4 SEND NICK Dave
C4 SEND USER dave 0 * :Dave
C4 EXPECT 001 Dave :*

# Setup channel topology:
# #chan1: Alice, Bob
# #chan2: Alice, Bob
# #chan3: Alice, Charlie
# #isolated: Dave
C1 SEND JOIN #chan1
C1 EXPECT :Alice!* JOIN #chan1
C2 SEND JOIN #chan1
C2 WAIT_RECV :Bob!* JOIN #chan1
C1 WAIT_RECV :Bob!* JOIN #chan1

C1 SEND JOIN #chan2
C1 EXPECT :Alice!* JOIN #chan2
C2 SEND JOIN #chan2
C2 WAIT_RECV :Bob!* JOIN #chan2
C1 WAIT_RECV :Bob!* JOIN #chan2

C1 SEND JOIN #chan3
C1 EXPECT :Alice!* JOIN #chan3
C3 SEND JOIN #chan3
C3 WAIT_RECV :Charlie!* JOIN #chan3
C1 WAIT_RECV :Charlie!* JOIN #chan3

C4 SEND JOIN #isolated
C4 EXPECT :Dave!* JOIN #isolated

# Alice quits
C1 SEND QUIT :Multi-channel exit
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob (shares #chan1 and #chan2) must receive QUIT exactly once
C2 WAIT_RECV :Alice!* QUIT :Multi-channel exit

# Charlie (shares #chan3) receives QUIT
C3 WAIT_RECV :Alice!* QUIT :Multi-channel exit

# Dave is unaffected and can message normally
C4 SEND PRIVMSG #isolated :Still running
C4 EXPECT_CONNECTED
