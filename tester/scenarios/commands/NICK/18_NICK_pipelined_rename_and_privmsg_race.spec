# 18_NICK_pipelined_rename_and_privmsg_race.spec
# Pipelined rename immediately followed by PRIVMSG in a single frame.
# Expected: Channel members receive the NICK announcement first, and the subsequent PRIVMSG arrives from the NEW nickname.
CLIENTS C1, C2

# C1 registers as Alice18
C1 SEND PASS 1234
C1 SEND NICK Alice18
C1 SEND USER user18 0 * :Alice 18
C1 EXPECT 001 Alice18 :*

# C2 registers as Bob18
C2 SEND PASS 1234
C2 SEND NICK Bob18
C2 SEND USER user18 0 * :Bob 18
C2 EXPECT 001 Bob18 :*

C1 SEND JOIN #race18
C2 SEND JOIN #race18
C1 WAIT_RECV :Bob18!* JOIN #race18

# C1 pipelines NICK and PRIVMSG together
C1 SEND_RAW NICK Alicia18\r\nPRIVMSG #race18 :Message from Alicia\r\n

# C2 must receive NICK change first, then PRIVMSG from Alicia18
C2 WAIT_RECV :Alice18!* NICK :Alicia18
C2 WAIT_RECV :Alicia18!* PRIVMSG #race18 :Message from Alicia
