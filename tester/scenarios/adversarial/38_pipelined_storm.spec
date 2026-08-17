# Tests pipelined multi-command bursts (ADV-NET-04) and parameter list overflows (ADV-FUZZ-02).
CLIENTS C1, C2

# C2 standard registration
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# ADV-NET-04: C1 pipelines full registration and multiple channel commands in a single raw TCP buffer
C1 SEND_RAW PASS 1234\r\nNICK Alice\r\nUSER alice 0 * :Alice\r\nJOIN #storm\r\nPRIVMSG #storm :Pipelined Hello\r\nMODE #storm +t\r\n
C1 EXPECT 001 Alice :*
C1 EXPECT :Alice!* JOIN #storm
C1 EXPECT :Alice!* MODE #storm +t

# Bob joins the channel created by the pipelined storm
C2 SEND JOIN #storm
C2 WAIT_RECV :Bob!* JOIN #storm
C1 WAIT_RECV :Bob!* JOIN #storm

# ADV-FUZZ-02: Massive parameter overflow (JOIN with many channels/parameters)
C1 SEND JOIN #c1 #c2 #c3 #c4 #c5 #c6 #c7 #c8 #c9 #c10
C1 EXPECT_CONNECTED

# Bounded message flood from C1
C1 FLOOD 10 PRIVMSG #storm :Burst message

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
