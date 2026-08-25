# 254_QUIT_spoofed_prefix_rejection.spec
# Tests that an adversary attempting to spoof another client's QUIT via prefix is rejected with 421 Unknown command.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Adversary tries to send client-prefixed command
C1 SEND :Bob QUIT :Spoofed exit
C1 EXPECT 421 Alice Unknown command.
C1 EXPECT_CONNECTED
