# 192_PING_interleaved_registration_pipeline.spec
# Tests pipelined registration commands interleaved with multiple PING requests in single TCP packet.
CLIENTS C1

C1 SEND_RAW PASS 1234\r\nPING probe1\r\nNICK Alice\r\nPING probe2\r\nUSER alice 0 * :Alice Smith\r\nPING probe3\r\n
C1 EXPECT :localhost PONG localhost :probe1
C1 EXPECT :localhost PONG localhost :probe2
C1 EXPECT 001 Alice :Welcome to ft_irc
C1 EXPECT 002 Alice :Your host is localhost
C1 EXPECT 003 Alice :This server was created today
C1 EXPECT 004 Alice localhost ft_irc 1.0 o o
C1 EXPECT :localhost PONG localhost :probe3
