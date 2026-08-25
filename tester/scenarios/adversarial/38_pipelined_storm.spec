# Tests pipelined multi-command bursts (ADV-NET-04) and parameter list overflows (ADV-FUZZ-02).
CLIENTS C1, C2

# C2 standard registration
C2 SEND PASS 1234
C2 SEND NICK Bob018
C2 SEND USER bob018 0 * :Bob018
C2 EXPECT 001 Bob018 :*

# ADV-NET-04: C1 pipelines full registration and multiple channel commands in a single raw TCP buffer
C1 SEND_RAW PASS 1234\r\nNICK Ali018\r\nUSER ali018 0 * :Ali018\r\nJOIN #storm\r\nPRIVMSG #storm :Pipelined Hello\r\nMODE #storm +t\r\n
C1 EXPECT 001 Ali018 :*
C1 EXPECT :Ali018!* JOIN #storm
C1 EXPECT :Ali018!* MODE #storm +t

# Bob joins the channel created by the pipelined storm
C2 SEND JOIN #storm
C2 WAIT_RECV :Bob018!* JOIN #storm
C1 WAIT_RECV :Bob018!* JOIN #storm

# ADV-FUZZ-02: Massive parameter overflow (JOIN with many channels/parameters)
C1 SEND JOIN #c1 #c2 #c3 #c4 #c5 #c6 #c7 #c8 #c9 #c10
C1 EXPECT_CONNECTED

# Bounded message flood from C1
C1 FLOOD 10 PRIVMSG #storm :Burst message

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
