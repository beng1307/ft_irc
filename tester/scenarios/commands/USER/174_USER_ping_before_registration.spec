# 174_USER_ping_before_registration.spec
# Tests that PING works for an unregistered client who has sent USER
CLIENTS C1

C1 SEND USER ali396 0 * :Ali396 Smith
C1 SEND PING testprobe
C1 EXPECT :localhost PONG localhost :testprobe
