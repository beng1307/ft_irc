# 32_JOIN_user_limit_enforcement.spec
# Tests channel user limit (+l) mode enforcement upon JOIN
# Expected:
# 1. Joins succeed while channel member count < limit.
# 2. When member count reaches limit, subsequent JOIN receives 471 Cannot join channel (+l).
# 3. When a member parts, a new client is able to join.
CLIENTS C1, C2, C3

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C3 registers as Charlie
C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# Alice creates #limited and sets limit +l 2
C1 SEND JOIN #limited
C1 SEND MODE #limited +l 2
C1 EXPECT :Alice!* MODE #limited +l 2

# Bob joins (channel now has 2 members: Alice, Bob)
C2 SEND JOIN #limited
C1 WAIT_RECV :Bob!* JOIN #limited

# Charlie attempts to join full channel (limit = 2) -> 471
C3 SEND JOIN #limited
C3 EXPECT 471 Charlie #limited :Cannot join channel (+l)

# Bob parts the channel (channel now has 1 member)
C2 SEND PART #limited :Leaving
C1 WAIT_RECV :Bob!* PART #limited*

# Charlie attempts to join again -> succeeds
C3 SEND JOIN #limited
C3 EXPECT :Charlie!* JOIN #limited
C1 WAIT_RECV :Charlie!* JOIN #limited
