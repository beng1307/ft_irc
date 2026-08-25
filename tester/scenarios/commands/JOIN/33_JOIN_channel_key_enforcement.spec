# 33_JOIN_channel_key_enforcement.spec
# Tests channel key (+k) mode enforcement upon JOIN
# Expected:
# 1. Joining a key-protected channel with no key or wrong key yields 475 Cannot join channel (+k).
# 2. Joining with the exact correct key succeeds.
# 3. After clearing +k, joining without a key succeeds.
CLIENTS C1, C2, C3

# C1 registers as Alice
C1 SEND PASS 1234
C1 SEND NICK Ali116
C1 SEND USER ali116 0 * :Ali116
C1 EXPECT 001 Ali116 :*

# C2 registers as Bob
C2 SEND PASS 1234
C2 SEND NICK Bob116
C2 SEND USER bob116 0 * :Bob116
C2 EXPECT 001 Bob116 :*

# C3 registers as Charlie
C3 SEND PASS 1234
C3 SEND NICK Cha116
C3 SEND USER cha116 0 * :Cha116
C3 EXPECT 001 Cha116 :*

# Alice creates #keychan and sets key +k hunter2
C1 SEND JOIN #keychan
C1 SEND MODE #keychan +k hunter2
C1 EXPECT :Ali116!* MODE #keychan +k hunter2

# Bob tries to join without a key -> 475
C2 SEND JOIN #keychan
C2 EXPECT 475 Bob116 #keychan :Cannot join channel (+k)

# Bob tries to join with the wrong key -> 475
C2 SEND JOIN #keychan wrongpassword
C2 EXPECT 475 Bob116 #keychan :Cannot join channel (+k)

# Bob joins with the correct key -> succeeds
C2 SEND JOIN #keychan hunter2
C2 EXPECT :Bob116!* JOIN #keychan
C1 WAIT_RECV :Bob116!* JOIN #keychan

# Alice clears key
C1 SEND MODE #keychan -k
C1 EXPECT :Ali116!* MODE #keychan -k*

# Charlie joins without a key -> succeeds
C3 SEND JOIN #keychan
C3 EXPECT :Cha116!* JOIN #keychan
C1 WAIT_RECV :Cha116!* JOIN #keychan
