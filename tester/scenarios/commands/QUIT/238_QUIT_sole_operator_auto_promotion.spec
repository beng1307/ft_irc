# 211_QUIT_sole_operator_auto_promotion.spec
# Tests that when the sole operator quits a multi-member channel, the remaining member is auto-promoted to operator and can execute op commands.
CLIENTS C1, C2

# Alice (op)
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Bob (regular)
C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C1 SEND JOIN #community
C1 EXPECT :Alice!* JOIN #community

C2 SEND JOIN #community
C2 WAIT_RECV :Bob!* JOIN #community
C1 WAIT_RECV :Bob!* JOIN #community

# Alice (the only operator) quits
C1 SEND QUIT :Admin signing off
C1 EXPECT ERROR :Closing connection
C1 EXPECT_DISCONNECT

C2 WAIT_RECV :Alice!* QUIT :Admin signing off

# Bob should now have operator privilege (can set invite-only mode)
C2 SEND MODE #community +i
C2 EXPECT :Bob!* MODE #community +i
