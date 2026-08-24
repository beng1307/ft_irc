# PRIVMSG with case variations in target nick.
# IRC nicks are case-insensitive - "alice", "ALICE", "Alice" are the same.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK AlIcE
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 * :*

C2 SEND PASS 1234
C2 SEND NICK BoB
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 * :*

# Message using different case
C1 SEND PRIVMSG bob :Lowercase
C2 WAIT_RECV :AlIcE!* PRIVMSG * :Lowercase

C1 SEND PRIVMSG BOB :Uppercase
C2 WAIT_RECV :AlIcE!* PRIVMSG * :Uppercase

C1 SEND PRIVMSG BoB :MixedCase
C2 WAIT_RECV :AlIcE!* PRIVMSG * :MixedCase

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
