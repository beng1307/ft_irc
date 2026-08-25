# 18_NICK_pipelined_rename_and_privmsg_race.spec
# Pipelined rename immediately followed by PRIVMSG in a single frame.
# Expected: Channel members receive the NICK announcement first, and the subsequent PRIVMSG arrives from the NEW nickname.
CLIENTS C1, C2

# C1 registers as Alice18
C1 SEND PASS 1234
C1 SEND NICK Ali200
C1 SEND USER u200 0 * :Ali200 18
C1 EXPECT 001 Ali200 :*

# C2 registers as Bob18
C2 SEND PASS 1234
C2 SEND NICK Bob200
C2 SEND USER u200 0 * :Bob200 18
C2 EXPECT 001 Bob200 :*

C1 SEND JOIN #race18
C2 SEND JOIN #race18
C1 WAIT_RECV :Bob200!* JOIN #race18

# C1 pipelines NICK and PRIVMSG together
C1 SEND_RAW NICK Ali200\r\nPRIVMSG #race18 :Message from Ali200\r\n

# C2 must receive NICK change first, then PRIVMSG from Alicia18
C2 WAIT_RECV :Ali200!* NICK :Ali200
C2 WAIT_RECV :Ali200!* PRIVMSG #race18 :Message from Ali200
