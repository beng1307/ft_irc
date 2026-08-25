# 52_MODE_nick_case_insensitivity.spec
# Tests case-insensitivity when targeting a user with +o (e.g. MODE #chan +o bob when registered as Bob)
# Expected: Server finds Bob and promotes them, broadcasting MODE #chan +o Bob (or bob).
# Bug: Exact case comparison in get_client causes 401 bob :No such nick/channel.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #chan
C1 EXPECT 353 Alice = #chan :@Alice
C1 EXPECT 366 Alice #chan :End of /NAMES list

C2 SEND JOIN #chan
C1 WAIT_RECV :Bob!* JOIN #chan

# Promote using lowercase nickname
C1 SEND MODE #chan +o bob
C1 EXPECT :Alice!* MODE #chan +o *
C2 EXPECT :Alice!* MODE #chan +o *
