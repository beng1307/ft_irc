# PRIVMSG to channel without joining it.
# Sender should either be able to message the channel or get an error.
# Different IRC servers handle this differently - test for consistency.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C2 joins #channel
C2 SEND JOIN #channel
C2 EXPECT :Bob!* JOIN #channel

# C1 sends message to #channel WITHOUT being a member
# RFC allows this; server should accept it
C1 SEND PRIVMSG #channel :Message from non-member
C2 WAIT_RECV :Alice!* PRIVMSG #channel :Message from non-member

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
