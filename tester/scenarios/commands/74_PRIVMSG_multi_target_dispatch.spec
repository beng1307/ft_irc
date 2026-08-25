# 44_PRIVMSG_multi_target_dispatch.spec
# Tests RFC 2812 §3.3.1 multi-target comma-separated PRIVMSG dispatch
# Expected: Both Bob and Charlie receive the message
# Bug: Server searches for a single target named "Bob,Charlie" and returns 401 ERR_NOSUCHNICK
CLIENTS C1, C2, C3

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

# Setup C3
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# C1 sends multi-target PRIVMSG
C1 SEND PRIVMSG Bob,Charlie :Hello team
C2 WAIT_RECV :Alice!* PRIVMSG Bob :Hello team
C3 WAIT_RECV :Alice!* PRIVMSG Charlie :Hello team
