# 205_QUIT_multi_word_without_colon.spec
# Tests that QUIT without a leading colon on multi-word reason takes the first argument.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali320
C1 SEND USER ali320 0 * :Ali320
C1 EXPECT 001 Ali320 :*

C2 SEND PASS 1234
C2 SEND NICK Bob320
C2 SEND USER bob320 0 * :Bob320
C2 EXPECT 001 Bob320 :*

C1 SEND JOIN #lobby
C1 EXPECT :Ali320!* JOIN #lobby

C2 SEND JOIN #lobby
C2 WAIT_RECV :Bob320!* JOIN #lobby
C1 WAIT_RECV :Bob320!* JOIN #lobby

# Alice quits without colon on multi-word input
C1 SEND QUIT Goodbye everyone!
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

# Bob receives first argument as reason
C2 WAIT_RECV :Ali320!* QUIT :Goodbye
C2 EXPECT_CONNECTED
