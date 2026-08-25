# 195_PING_rapid_pipelined_burst.spec
# Tests burst of 10 sequential PING commands to verify FIFO response ordering
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND PING req1
C1 SEND PING req2
C1 SEND PING req3
C1 SEND PING req4
C1 SEND PING req5
C1 EXPECT :localhost PONG localhost :req1
C1 EXPECT :localhost PONG localhost :req2
C1 EXPECT :localhost PONG localhost :req3
C1 EXPECT :localhost PONG localhost :req4
C1 EXPECT :localhost PONG localhost :req5
