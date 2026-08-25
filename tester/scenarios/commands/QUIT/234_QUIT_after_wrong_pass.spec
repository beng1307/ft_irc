# 207_QUIT_after_wrong_pass.spec
# Tests that an unregistered client that supplied an incorrect password can still quit cleanly.
CLIENTS C1

# C1 supplies wrong password
C1 SEND PASS wrongpassword
C1 SEND NICK Ali322
C1 SEND USER ali322 0 * :Ali322

# C1 quits
C1 SEND QUIT :Failed auth exit
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT
