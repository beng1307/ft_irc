# 51_PRIVMSG_self_messaging_echo.spec
# Tests unicast direct message sent to oneself (self-messaging / note)
# Expected: Sender receives the PRIVMSG back from server
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C1 sends PRIVMSG to Alice
C1 SEND PRIVMSG Alice :Self note
C1 WAIT_RECV :Alice!* PRIVMSG Alice :Self note
