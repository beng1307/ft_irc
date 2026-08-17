# Tests unauthenticated command gating (ADV-STATE-01), pre-auth nick hijack attempts (ADV-STATE-02), and double registration safety (ADV-MEM-05).
CLIENTS C1, C2

# ADV-STATE-01: Probing channel, messaging, and operator commands before PASS / registration -> must return 451
C1 SEND JOIN #secret
C1 EXPECT 451 * :*
C1 SEND MODE #secret +i
C1 EXPECT 451 * :*
C1 SEND TOPIC #secret :HackedTopic
C1 EXPECT 451 * :*
C1 SEND KICK #secret Bob :kick
C1 EXPECT 451 * :*
C1 SEND INVITE Bob #secret
C1 EXPECT 451 * :*
C1 SEND PRIVMSG #secret :hello
C1 EXPECT 451 * :*
C1 SEND PART #secret :part
C1 EXPECT 451 * :*

# ADV-STATE-02: Pre-auth nick claim without PASS -> cannot steal identity
C1 SEND NICK AdminUser
C1 EXPECT_NONE 150ms

# C2 authenticates properly with PASS and takes AdminUser
C2 SEND PASS 1234
C2 SEND NICK AdminUser
C2 SEND USER admin 0 * :Admin User
C2 EXPECT 001 AdminUser :*

# C1 now registers with valid credentials and distinct nickname
C1 SEND PASS 1234
C1 SEND NICK AliceUnauth
C1 SEND USER alice 0 * :Alice Unauth
C1 EXPECT 001 AliceUnauth :*

# ADV-MEM-05: Double registration attempts after successful authentication -> 462
C1 SEND PASS 1234
C1 EXPECT 462 AliceUnauth :*
C1 SEND USER alice2 0 * :Alice Two
C1 EXPECT 462 AliceUnauth :*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
