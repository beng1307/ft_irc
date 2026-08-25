# 254_QUIT_spoofed_prefix_rejection.spec
# Tests that an adversary attempting to spoof another client's QUIT via prefix is rejected with 421 Unknown command.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali342
C1 SEND USER ali342 0 * :Ali342
C1 EXPECT 001 Ali342 :*

# Adversary tries to send client-prefixed command
C1 SEND :Bob342 QUIT :Spoofed exit
C1 EXPECT 421 Ali342 Unknown command.
C1 EXPECT_CONNECTED
