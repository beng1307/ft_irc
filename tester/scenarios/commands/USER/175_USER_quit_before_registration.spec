# 175_USER_quit_before_registration.spec
# Tests clean QUIT disconnection when only USER was sent
CLIENTS C1

C1 SEND USER ali397 0 * :Ali397 Smith
C1 SEND QUIT :Goodbye
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECTED
