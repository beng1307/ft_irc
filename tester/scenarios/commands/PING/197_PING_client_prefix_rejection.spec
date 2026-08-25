# 197_PING_client_prefix_rejection.spec
# Tests client sending a message with leading client prefix (e.g. :Alice PING 12345)
# Expected Behavior: Handled or returns 421 Unknown command because prefix token is not stripped
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice Smith
C1 EXPECT 001 Alice :*

C1 SEND :Alice PING 12345
C1 EXPECT 421 * :prefix Unknown command.
