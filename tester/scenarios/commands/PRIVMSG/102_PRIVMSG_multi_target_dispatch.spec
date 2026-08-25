# 102_PRIVMSG_multi_target_dispatch.spec
# Tests RFC 2812 §3.3.1 multi-target comma-separated PRIVMSG dispatch
# Expected: Both Bob and Charlie receive the message
# Bug: Server searches for a single target named "Bob,Charlie" and returns 401 ERR_NOSUCHNICK
CLIENTS C1, C2, C3

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Ali287
C1 SEND USER ali287 0 * :Ali287
C1 EXPECT 001 Ali287 :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob287
C2 SEND USER bob287 0 * :Bob287
C2 EXPECT 001 Bob287 :*

# Setup C3
C3 SEND PASS 1234
C3 SEND NICK Cha287
C3 SEND USER cha287 0 * :Cha287
C3 EXPECT 001 Cha287 :*

# C1 sends multi-target PRIVMSG
C1 SEND PRIVMSG Bob287,Cha287 :Hello team
C2 WAIT_RECV :Ali287!* PRIVMSG Bob287 :Hello team
C3 WAIT_RECV :Ali287!* PRIVMSG Cha287 :Hello team
