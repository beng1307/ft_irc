# Scenario 45: Pipelined Commands with Embedded QUIT
# Tests execution of pipelined stream containing a mid-stream QUIT to verify safe client erasure
CLIENTS C1, C2

# Register Alice normally
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Alice creates #pipelinechan
C1 SEND JOIN #pipelinechan
C1 EXPECT :Alice!* JOIN #pipelinechan

# Bob sends PASS, NICK, USER, JOIN, QUIT, and extra commands in a single raw TCP write
C2 SEND_RAW PASS 1234\r\nNICK Bob\r\nUSER bob 0 * :Bob\r\nJOIN #pipelinechan\r\nQUIT :Pipelined Goodbye\r\nPRIVMSG #pipelinechan :Ghost\r\n

# Alice sees Bob join and quit cleanly
C1 WAIT_RECV :Bob!* JOIN #pipelinechan
C1 WAIT_RECV :Bob!* QUIT :Pipelined Goodbye

# Verify C2 is disconnected
C2 EXPECT_DISCONNECT

# Alice and server continue normally
C1 SEND PRIVMSG #pipelinechan :Alice is still running
C1 EXPECT_CONNECTED
