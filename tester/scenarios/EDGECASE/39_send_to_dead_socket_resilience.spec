# Scenario 39: Send to Dead Socket Resilience
# Tests server stability when broadcasting to a channel where a member abruptly drops (RST/closed)
CLIENTS C1, C2, C3

# Register 3 clients
C1 SEND PASS 1234
C1 SEND NICK Ali001
C1 SEND USER ali001 0 * :Ali001
C1 EXPECT 001 Ali001 :*

C2 SEND PASS 1234
C2 SEND NICK Bob001
C2 SEND USER bob001 0 * :Bob001
C2 EXPECT 001 Bob001 :*

C3 SEND PASS 1234
C3 SEND NICK Cha001
C3 SEND USER cha001 0 * :Cha001
C3 EXPECT 001 Cha001 :*

# All 3 join #deadsocket
C1 SEND JOIN #deadsocket
C1 EXPECT :Ali001!* JOIN #deadsocket
C2 SEND JOIN #deadsocket
C2 WAIT_RECV :Bob001!* JOIN #deadsocket
C3 SEND JOIN #deadsocket
C3 WAIT_RECV :Cha001!* JOIN #deadsocket

# Charlie abruptly drops connection with RST
C3 RESET

# Alice broadcasts to #deadsocket; Bob must receive and server must stay healthy
C1 SEND PRIVMSG #deadsocket :Message after Cha001 dropped
C2 WAIT_RECV :Ali001!* PRIVMSG #deadsocket :Message after Cha001 dropped

# Bob replies
C2 SEND PRIVMSG #deadsocket :Bob001 is still alive
C1 WAIT_RECV :Bob001!* PRIVMSG #deadsocket :Bob001 is still alive

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
