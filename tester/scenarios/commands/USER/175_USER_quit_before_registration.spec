# 175_USER_quit_before_registration.spec
# Tests clean QUIT disconnection when only USER was sent
CLIENTS C1

C1 SEND USER alice 0 * :Alice Smith
C1 SEND QUIT :Goodbye
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECTED
