# 49_MODE_nick_case_insensitivity.spec
# Tests case-insensitivity when targeting a user with +o (e.g. MODE #chan +o bob when registered as Bob)
# Expected: Server finds Bob and promotes them, broadcasting MODE #chan +o Bob (or bob).
# Bug: Exact case comparison in get_client causes 401 bob :No such nick/channel.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali166
C1 SEND USER ali166 0 * :Ali166
C1 EXPECT 001 Ali166 :*

C2 SEND PASS 1234
C2 SEND NICK Bob166
C2 SEND USER bob166 0 * :Bob166
C2 EXPECT 001 Bob166 :*

C1 SEND JOIN #chan
C1 EXPECT 353 Ali166 = #chan :@Ali166
C1 EXPECT 366 Ali166 #chan :End of /NAMES list

C2 SEND JOIN #chan
C1 WAIT_RECV :Bob166!* JOIN #chan

# Promote using lowercase nickname
C1 SEND MODE #chan +o bob166
C1 EXPECT :Ali166!* MODE #chan +o *
C2 EXPECT :Ali166!* MODE #chan +o *
