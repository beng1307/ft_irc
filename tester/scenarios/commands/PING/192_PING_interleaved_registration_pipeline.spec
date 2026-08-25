# 192_PING_interleaved_registration_pipeline.spec
# Tests pipelined registration commands interleaved with multiple PING requests in single TCP packet.
CLIENTS C1

C1 SEND_RAW PASS 1234\r\nPING probe1\r\nNICK Ali278\r\nPING probe2\r\nUSER ali278 0 * :Ali278 Smith\r\nPING probe3\r\n
C1 EXPECT :localhost PONG localhost :probe1
C1 EXPECT :localhost PONG localhost :probe2
C1 EXPECT 001 Ali278 :Welcome to ft_irc
C1 EXPECT 002 Ali278 :Your host is localhost
C1 EXPECT 003 Ali278 :This server was created today
C1 EXPECT 004 Ali278 localhost ft_irc 1.0 o o
C1 EXPECT :localhost PONG localhost :probe3
