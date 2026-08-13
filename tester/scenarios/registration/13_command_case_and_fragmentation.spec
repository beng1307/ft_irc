# Mixed-case commands and several commands in fragmented TCP input are parsed independently.
CLIENTS C1

C1 SEND pass 1234
C1 SEND_RAW ni
C1 SEND_RAW ck Alice\r\nuser alice 0 * :Alice\r\n
C1 EXPECT 001 Alice :Welcome to ft_irc
C1 EXPECT_CONNECTED
