# 215_QUIT_part_then_quit_no_leak.spec
# Tests that if a client sends PART followed by QUIT, ex-channel members do not receive duplicate/stale QUIT broadcast.
CLIENTS C1, C2

# Alice (C1) and Bob (C2) in #partquit
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #partquit
C1 EXPECT :Alice!* JOIN #partquit

C2 SEND JOIN #partquit
C2 WAIT_RECV :Bob!* JOIN #partquit
C1 WAIT_RECV :Bob!* JOIN #partquit

# Bob parts #partquit, then sends QUIT
C2 SEND PART #partquit :Parting first
C2 EXPECT :Bob!* PART #partquit :Parting first
C1 WAIT_RECV :Bob!* PART #partquit :Parting first

C2 SEND QUIT :Now quitting server
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECT

# Alice receives no QUIT broadcast because they share 0 mutual channels now
C1 SEND PRIVMSG #partquit :Are you still there?
C1 EXPECT_CONNECTED
