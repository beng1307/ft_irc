# 19_NICK_unauthenticated_eviction_attempt.spec
# Unauthenticated attacker attempts to steal or evict an active registered client's nickname.
# Expected: Attacker is rejected with 433 Nickname is already in use; registered client stays connected and unharmed.
CLIENTS C1, C2

# C1 registers as Alice19
C1 SEND PASS 1234
C1 SEND NICK Alice19
C1 SEND USER user19 0 * :Alice 19
C1 EXPECT 001 Alice19 :*

# C2 attempts to claim 'Alice19' without PASS
C2 SEND NICK Alice19
C2 EXPECT 433 * Alice19 :Nickname is already in use

# C2 attempts to claim 'Alice19' with wrong PASS
C2 SEND PASS wrong
C2 EXPECT 464 * :Password incorrect
C2 SEND NICK Alice19
C2 EXPECT 433 * Alice19 :Nickname is already in use

# C1 remains connected and fully operational
C1 SEND PING localhost
C1 EXPECT :localhost PONG localhost :localhost
C1 EXPECT_CONNECTED
