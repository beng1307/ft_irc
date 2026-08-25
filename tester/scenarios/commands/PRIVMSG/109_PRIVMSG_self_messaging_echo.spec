# 109_PRIVMSG_self_messaging_echo.spec
# Tests unicast direct message sent to oneself (self-messaging / note)
# Expected: Sender receives the PRIVMSG back from server
CLIENTS C1

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali294
C1 SEND USER ali294 0 * :Ali294
C1 EXPECT 001 Ali294 :*

# C1 sends PRIVMSG to Alice
C1 SEND PRIVMSG Ali294 :Self note
C1 WAIT_RECV :Ali294!* PRIVMSG Ali294 :Self note
