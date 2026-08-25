# 194_PING_quit_pipeline_rejection.spec
# Tests pipelined QUIT followed by PING in the same TCP buffer (QUIT :bye\r\nPING afterquit\r\n)
# Expected Behavior: Server sends 'ERROR :Closing connection' and closes socket without executing PING
# Flaw: Server continues parsing remaining buffer and sends 'PONG localhost :afterquit' AFTER ERROR
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND_RAW QUIT :Leaving\r\nPING afterquit\r\n
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT
