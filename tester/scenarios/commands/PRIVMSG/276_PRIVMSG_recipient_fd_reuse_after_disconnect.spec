# 276_PRIVMSG_recipient_fd_reuse_after_disconnect.spec
# State Corruption / FD Reuse: C2 disconnects; new client C3 gets assigned C2's former FD.
# C1 sends PRIVMSG to C2's old nickname 'Bob'.
# Expected: Server replies 401 ERR_NOSUCHNICK (Bob :No such nick/channel); C3 (Charlie) receives nothing.
CLIENTS C1, C2, C3

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2 (Bob)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C2 disconnects
C2 SEND QUIT :Leaving
C2 EXPECT ERROR :Closing connection
C2 EXPECT_DISCONNECTED

# C3 connects and registers as Charlie
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# C1 attempts to send message to Bob
C1 SEND PRIVMSG Bob :Are you still there Bob?
C1 EXPECT 401 Alice Bob :No such nick/channel
C3 NO_RECV :Alice!* PRIVMSG Bob :Are you still there Bob?
