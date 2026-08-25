# 40_PRIVMSG_multi_word_without_colon.spec
# Tests PRIVMSG with multiple words without leading colon on payload
# Expected: Server delivers the entire text "hello world from alice" to recipient
# Bug: Server only takes arguments[1] ("hello"), silently dropping all trailing words ("world from alice")
CLIENTS C1, C2

# Setup C1
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Setup C2
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Join channel
C1 SEND JOIN #chan
C1 EXPECT 366 Alice #chan :End of /NAMES list
C2 SEND JOIN #chan
C1 WAIT_RECV :Bob!* JOIN #chan

# C1 sends multi-word message without colon
C1 SEND PRIVMSG #chan hello world from alice
C2 WAIT_RECV :Alice!* PRIVMSG #chan :hello world from alice
