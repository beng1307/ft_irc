# 32_JOIN_user_limit_enforcement.spec
# Tests channel user limit (+l) mode enforcement upon JOIN
# Expected:
# 1. Joins succeed while channel member count < limit.
# 2. When member count reaches limit, subsequent JOIN receives 471 Cannot join channel (+l).
# 3. When a member parts, a new client is able to join.
CLIENTS C1, C2, C3

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Ali115
C1 SEND USER ali115 0 * :Ali115
C1 EXPECT 001 Ali115 :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob115
C2 SEND USER bob115 0 * :Bob115
C2 EXPECT 001 Bob115 :*

# C3 registers as Charlie
C3 SEND PASS 1234
C3 SEND NICK Cha115
C3 SEND USER cha115 0 * :Cha115
C3 EXPECT 001 Cha115 :*

# Alice creates #limited and sets limit +l 2
C1 SEND JOIN #limited
C1 SEND MODE #limited +l 2
C1 EXPECT :Ali115!* MODE #limited +l 2

# Bob joins (channel now has 2 members: Alice, Bob)
C2 SEND JOIN #limited
C1 WAIT_RECV :Bob115!* JOIN #limited

# Charlie attempts to join full channel (limit = 2) -> 471
C3 SEND JOIN #limited
C3 EXPECT 471 Cha115 #limited :Cannot join channel (+l)

# Bob parts the channel (channel now has 1 member)
C2 SEND PART #limited :Leaving
C1 WAIT_RECV :Bob115!* PART #limited*

# Charlie attempts to join again -> succeeds
C3 SEND JOIN #limited
C3 EXPECT :Cha115!* JOIN #limited
C1 WAIT_RECV :Cha115!* JOIN #limited
