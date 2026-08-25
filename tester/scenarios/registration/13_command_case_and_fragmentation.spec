# Mixed-case commands and several commands in fragmented TCP input are parsed independently.
CLIENTS C1

C1 SEND pass 1234
C1 SEND_RAW ni
C1 SEND_RAW ck Ali452\r\nuser ali452 0 * :Ali452\r\n
C1 EXPECT 001 Ali452 :Welcome to ft_irc
C1 EXPECT_CONNECTED
