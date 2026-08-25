# 198_PING_fragmented_tcp_frames.spec
# Tests fragmented TCP arrival of PING command across multiple small chunks
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND_RAW PIN
C1 WAIT 50ms
C1 SEND_RAW G fr
C1 WAIT 50ms
C1 SEND_RAW agment_test\r
C1 WAIT 50ms
C1 SEND_RAW \n
C1 EXPECT :localhost PONG localhost :fragment_test
