# 17_NICK_rapid_rename_burst_pipeline.spec
# Malicious actor sends a rapid burst of pipelined NICK changes in a single TCP packet.
# Expected: Server processes all state transitions cleanly, broadcasts each rename in order to shared channel members, and ends up in FinalNick17.
CLIENTS C1, C2

# C1 registers as Alice17
C1 SEND PASS 1234
C1 SEND NICK Alice17
C1 SEND USER user17 0 * :Alice 17
C1 EXPECT 001 Alice17 :*

# C2 registers as Bob17
C2 SEND PASS 1234
C2 SEND NICK Bob17
C2 SEND USER user17 0 * :Bob 17
C2 EXPECT 001 Bob17 :*

# Both join #rapid17
C1 SEND JOIN #rapid17
C2 SEND JOIN #rapid17
C1 WAIT_RECV :Bob17!* JOIN #rapid17

# C1 bursts 5 rapid renames in a single packet
C1 SEND_RAW NICK NickOne17\r\nNICK NickTwo17\r\nNICK Nick3_17\r\nNICK NickFour17\r\nNICK Final17\r\n

# C2 must receive all broadcasts in order
C2 WAIT_RECV :Alice17!* NICK :NickOne17
C2 WAIT_RECV :NickOne17!* NICK :NickTwo17
C2 WAIT_RECV :NickTwo17!* NICK :Nick3_17
C2 WAIT_RECV :Nick3_17!* NICK :NickFour17
C2 WAIT_RECV :NickFour17!* NICK :Final17

# C1 is now Final17 and can communicate
C1 SEND PRIVMSG #rapid17 :All done
C2 WAIT_RECV :Final17!* PRIVMSG #rapid17 :All done

