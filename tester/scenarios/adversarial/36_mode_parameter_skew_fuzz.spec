# Tests mode flag & parameter mismatch fuzzing (ADV-FUZZ-04), limit overflow (ADV-FUZZ-05), and last-op demotion (ADV-STATE-04).
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# C1 creates channel and C2 joins
C1 SEND JOIN #modefuzz
C1 EXPECT :Alice!* JOIN #modefuzz
C2 SEND JOIN #modefuzz
C2 WAIT_RECV :Bob!* JOIN #modefuzz
C1 WAIT_RECV :Bob!* JOIN #modefuzz

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
C1 SEND MODE #modefuzz -o Alice
C1 WAIT_RECV :Alice!* MODE #modefuzz -o Alice
C2 WAIT_RECV :Alice!* MODE #modefuzz -o Alice

# Now #modefuzz has 0 operators: op-only commands should fail with 482 without crashing
C1 SEND KICK #modefuzz Bob :Cannot kick without op
C1 EXPECT 482 Alice #modefuzz :*

C2 SEND KICK #modefuzz Alice :Cannot kick without op
C2 EXPECT 482 Bob #modefuzz :*

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
