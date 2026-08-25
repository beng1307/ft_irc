# 270_PRIVMSG_pipelined_part_then_privmsg_race.spec
# Race Condition: Pipelining PART and PRIVMSG in the same TCP buffer
# Client sends 'PART #chan\r\nPRIVMSG #chan :Hello\r\n' in one burst.
# Expected: PART leaves channel immediately; subsequent PRIVMSG in same buffer is rejected with 442/404.
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Both join #channel
C1 SEND JOIN #channel
C1 EXPECT 366 Alice #channel :End of /NAMES list
C2 SEND JOIN #channel
C1 WAIT_RECV :Bob!* JOIN #channel

# C1 sends pipelined PART and PRIVMSG
C1 SEND_RAW PART #channel\r\nPRIVMSG #channel :I should not be able to talk\r\n
C2 WAIT_RECV :Alice!* PART #channel
C1 EXPECT 404 Alice #channel :*
C2 NO_RECV :Alice!* PRIVMSG #channel :I should not be able to talk
