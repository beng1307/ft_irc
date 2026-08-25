# 276_PRIVMSG_recipient_fd_reuse_after_disconnect.spec
# State Corruption / FD Reuse: C2 disconnects; new client C3 gets assigned C2's former FD.
# C1 sends PRIVMSG to C2's old nickname 'Bob'.
# Expected: Server replies 401 ERR_NOSUCHNICK (Bob :No such nick/channel); C3 (Charlie) receives nothing.
CLIENTS C1, C2, C3

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali308
C1 SEND USER ali308 0 * :Ali308
C1 EXPECT 001 Ali308 :*

# Setup C2 (Bob)
C2 SEND PASS 1234
C2 SEND NICK Bob308
C2 SEND USER bob308 0 * :Bob308
C2 EXPECT 001 Bob308 :*

# C2 disconnects
C2 SEND QUIT :Leaving
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECTED

# C3 connects and registers as Charlie
C3 SEND PASS 1234
C3 SEND NICK Cha308
C3 SEND USER cha308 0 * :Cha308
C3 EXPECT 001 Cha308 :*

# C1 attempts to send message to Bob
C1 SEND PRIVMSG Bob308 :Are you still there Bob308?
C1 EXPECT 401 Ali308 Bob308 :No such nick/channel
C3 NO_RECV :Ali308!* PRIVMSG Bob308 :Are you still there Bob308?
