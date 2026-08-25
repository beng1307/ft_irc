# Tests mode flag & parameter mismatch fuzzing (ADV-FUZZ-04), limit overflow (ADV-FUZZ-05), and last-op demotion (ADV-STATE-04).
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali016
C1 SEND USER ali016 0 * :Ali016
C1 EXPECT 001 Ali016 :*

C2 SEND PASS 1234
C2 SEND NICK Bob016
C2 SEND USER bob016 0 * :Bob016
C2 EXPECT 001 Bob016 :*

# C1 creates channel and C2 joins
C1 SEND JOIN #modefuzz
C1 EXPECT :Ali016!* JOIN #modefuzz
C2 SEND JOIN #modefuzz
C2 WAIT_RECV :Bob016!* JOIN #modefuzz
C1 WAIT_RECV :Bob016!* JOIN #modefuzz

# ADV-FUZZ-04: Mode flag & parameter mismatch fuzzing (must not crash, OOB read, or segfault)
C1 SEND MODE #modefuzz +itklo
C1 EXPECT_CONNECTED

C1 SEND MODE #modefuzz +k
C1 EXPECT_CONNECTED

C1 SEND MODE #modefuzz +o
C1 EXPECT_CONNECTED

C1 SEND MODE #modefuzz +l
C1 EXPECT_CONNECTED

C1 SEND MODE #modefuzz -o
C1 EXPECT_CONNECTED

# ADV-FUZZ-05: Integer limit mode fuzzing (very large, negative, and zero values)
C1 SEND MODE #modefuzz +l 999999999999999999999999999999
C1 EXPECT_CONNECTED

C1 SEND MODE #modefuzz +l -42
C1 EXPECT_CONNECTED

C1 SEND MODE #modefuzz +l 0
C1 EXPECT_CONNECTED

# ADV-STATE-04: Last-operator self-demotion / abandonment
C1 SEND MODE #modefuzz -o Ali016
C1 WAIT_RECV :Ali016!* MODE #modefuzz -o Ali016
C2 WAIT_RECV :Ali016!* MODE #modefuzz -o Ali016

# Now #modefuzz has 0 operators: op-only commands should fail with 482 without crashing
C1 SEND KICK #modefuzz Bob016 :Cannot kick without op
C1 EXPECT 482 Ali016 #modefuzz :*

C2 SEND KICK #modefuzz Ali016 :Cannot kick without op
C2 EXPECT 482 Bob016 #modefuzz :*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
