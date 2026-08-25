# 221_PASS_ping_before_pass_allowed.spec
# PING before PASS / registration is allowed by RFC 2812 to check server responsiveness
CLIENTS C1

C1 SEND PING localhost
C1 EXPECT :localhost PONG localhost :localhost

C1 SEND PASS 1234
C1 SEND NICK PAlice221
C1 SEND USER alice221 0 * :Alice Smith
C1 EXPECT 001 PAlice221 :*
