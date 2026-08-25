# 270_PRIVMSG_pipelined_part_then_privmsg_race.spec
# Race Condition: Pipelining PART and PRIVMSG in the same TCP buffer
# Client sends 'PART #chan\r\nPRIVMSG #chan :Hello\r\n' in one burst.
# Expected: PART leaves channel immediately; subsequent PRIVMSG in same buffer is rejected with 442/404.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali302
C1 SEND USER ali302 0 * :Ali302
C1 EXPECT 001 Ali302 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob302
C2 SEND USER bob302 0 * :Bob302
C2 EXPECT 001 Bob302 :*

# Both join #channel
C1 SEND JOIN #channel
C1 EXPECT 366 Ali302 #channel :End of /NAMES list
C2 SEND JOIN #channel
C1 WAIT_RECV :Bob302!* JOIN #channel

# C1 sends pipelined PART and PRIVMSG
C1 SEND_RAW PART #channel\r\nPRIVMSG #channel :I should not be able to talk\r\n
C2 WAIT_RECV :Ali302!* PART #channel
C1 EXPECT 404 Ali302 #channel :*
C2 NO_RECV :Ali302!* PRIVMSG #channel :I should not be able to talk
