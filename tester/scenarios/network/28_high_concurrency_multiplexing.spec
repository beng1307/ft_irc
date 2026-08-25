# Validates simultaneous multiplexing across 10 concurrent active client connections.
CLIENTS C1, C2, C3, C4, C5, C6, C7, C8, C9, C10

# Register all 10 clients concurrently
C1 SEND PASS 1234
C1 SEND NICK Usr1_28
C1 SEND USER u1_28 0 * :Usr447 One
C1 EXPECT 001 Usr1_28 :*

C2 SEND PASS 1234
C2 SEND NICK Usr2_28
C2 SEND USER u2_28 0 * :Usr447 Two
C2 EXPECT 001 Usr2_28 :*

C3 SEND PASS 1234
C3 SEND NICK Usr3_28
C3 SEND USER u3_28 0 * :Usr447 Three
C3 EXPECT 001 Usr3_28 :*

C4 SEND PASS 1234
C4 SEND NICK Usr4_28
C4 SEND USER u4_28 0 * :Usr447 Four
C4 EXPECT 001 Usr4_28 :*

C5 SEND PASS 1234
C5 SEND NICK Usr5_28
C5 SEND USER u5_28 0 * :Usr447 Five
C5 EXPECT 001 Usr5_28 :*

C6 SEND PASS 1234
C6 SEND NICK Usr6_28
C6 SEND USER u6_28 0 * :Usr447 Six
C6 EXPECT 001 Usr6_28 :*

C7 SEND PASS 1234
C7 SEND NICK Usr7_28
C7 SEND USER u7_28 0 * :Usr447 Seven
C7 EXPECT 001 Usr7_28 :*

C8 SEND PASS 1234
C8 SEND NICK Usr8_28
C8 SEND USER u8_28 0 * :Usr447 Eight
C8 EXPECT 001 Usr8_28 :*

C9 SEND PASS 1234
C9 SEND NICK Usr9_28
C9 SEND USER u9_28 0 * :Usr447 Nine
C9 EXPECT 001 Usr9_28 :*
C10 SEND PASS 1234
C10 SEND NICK Usr10_28
C10 SEND USER u1_280_28 0 * :Usr447 Ten
C10 EXPECT 001 Usr10_28 :*

# All 10 join shared broadcast channel
C1 SEND JOIN #concurrency
C2 SEND JOIN #concurrency
C3 SEND JOIN #concurrency
C4 SEND JOIN #concurrency
C5 SEND JOIN #concurrency
C6 SEND JOIN #concurrency
C7 SEND JOIN #concurrency
C8 SEND JOIN #concurrency
C9 SEND JOIN #concurrency
C10 SEND JOIN #concurrency
C10 WAIT_RECV :Usr10_28!* JOIN #concurrency
C1 WAIT_RECV :Usr10_28!* JOIN #concurrency

# Cross-client message validation
C1 SEND PRIVMSG #concurrency :Broadcast to all 10
C10 WAIT_RECV :Usr1_28!* PRIVMSG #concurrency :Broadcast to all 10
C5 WAIT_RECV :Usr1_28!* PRIVMSG #concurrency :Broadcast to all 10
C2 WAIT_RECV :Usr1_28!* PRIVMSG #concurrency :Broadcast to all 10

C1 EXPECT_CONNECTED
C10 EXPECT_CONNECTED
