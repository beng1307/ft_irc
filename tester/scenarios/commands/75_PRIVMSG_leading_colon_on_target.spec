# 45_PRIVMSG_leading_colon_on_target.spec
# Tests PRIVMSG with leading colon on the target parameter (e.g. PRIVMSG :Bob :Hello)
# Expected: Message is delivered to Bob
# Bug: Server treats ':Bob' as literal nickname and returns 401 :No such nick/channel
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 sends PRIVMSG with leading colon on recipient
C1 SEND PRIVMSG :Bob :Hello Bob
C2 WAIT_RECV :Alice!* PRIVMSG Bob :Hello Bob
