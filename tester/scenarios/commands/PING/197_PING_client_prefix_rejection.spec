# 197_PING_client_prefix_rejection.spec
# Tests client sending a message with leading client prefix (e.g. :Alice PING 12345)
# Expected Behavior: Handled or returns 421 Unknown command because prefix token is not stripped
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali283
C1 SEND USER ali283 0 * :Ali283 Smith
C1 EXPECT 001 Ali283 :*

C1 SEND :Ali283 PING 12345
C1 EXPECT 421 Ali283 Unknown command.
