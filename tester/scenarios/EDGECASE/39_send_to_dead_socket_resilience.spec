# Scenario 39: Send to Dead Socket Resilience
# Tests server stability when broadcasting to a channel where a member abruptly drops (RST/closed)
CLIENTS C1, C2, C3

# Register 3 clients
C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

C3 SEND PASS 1234
C3 SEND NICK Charlie
C3 SEND USER charlie 0 * :Charlie
C3 EXPECT 001 Charlie :*

# All 3 join #deadsocket
C1 SEND JOIN #deadsocket
C1 EXPECT :Alice!* JOIN #deadsocket
C2 SEND JOIN #deadsocket
C2 WAIT_RECV :Bob!* JOIN #deadsocket
C3 SEND JOIN #deadsocket
C3 WAIT_RECV :Charlie!* JOIN #deadsocket

# Charlie abruptly drops connection with RST
C3 RESET

# Alice broadcasts to #deadsocket; Bob must receive and server must stay healthy
C1 SEND PRIVMSG #deadsocket :Message after Charlie dropped
C2 WAIT_RECV :Alice!* PRIVMSG #deadsocket :Message after Charlie dropped

# Bob replies
C2 SEND PRIVMSG #deadsocket :Bob is still alive
C1 WAIT_RECV :Bob!* PRIVMSG #deadsocket :Bob is still alive

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
