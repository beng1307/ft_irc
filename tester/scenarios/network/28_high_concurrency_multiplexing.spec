# Validates simultaneous multiplexing across 10 concurrent active client connections.
CLIENTS C1, C2, C3, C4, C5, C6, C7, C8, C9, C10

# Register all 10 clients concurrently
C1 SEND PASS 1234
C1 SEND NICK User1
C1 SEND USER u1 0 * :User One
C1 EXPECT 001 User1 :*

C2 SEND PASS 1234
C2 SEND NICK User2
C2 SEND USER u2 0 * :User Two
C2 EXPECT 001 User2 :*

C3 SEND PASS 1234
C3 SEND NICK User3
C3 SEND USER u3 0 * :User Three
C3 EXPECT 001 User3 :*

C4 SEND PASS 1234
C4 SEND NICK User4
C4 SEND USER u4 0 * :User Four
C4 EXPECT 001 User4 :*

C5 SEND PASS 1234
C5 SEND NICK User5
C5 SEND USER u5 0 * :User Five
C5 EXPECT 001 User5 :*

C6 SEND PASS 1234
C6 SEND NICK User6
C6 SEND USER u6 0 * :User Six
C6 EXPECT 001 User6 :*

C7 SEND PASS 1234
C7 SEND NICK User7
C7 SEND USER u7 0 * :User Seven
C7 EXPECT 001 User7 :*

C8 SEND PASS 1234
C8 SEND NICK User8
C8 SEND USER u8 0 * :User Eight
C8 EXPECT 001 User8 :*

C9 SEND PASS 1234
C9 SEND NICK User9
C9 SEND USER u9 0 * :User Nine
C9 EXPECT 001 User9 :*
C10 SEND PASS 1234
C10 SEND NICK User10
C10 SEND USER u10 0 * :User Ten
C10 EXPECT 001 User10 :*

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
C10 WAIT_RECV :User10!* JOIN #concurrency
C1 WAIT_RECV :User10!* JOIN #concurrency

# Cross-client message validation
C1 SEND PRIVMSG #concurrency :Broadcast to all 10
C10 WAIT_RECV :User1!* PRIVMSG #concurrency :Broadcast to all 10
C5 WAIT_RECV :User1!* PRIVMSG #concurrency :Broadcast to all 10
C2 WAIT_RECV :User1!* PRIVMSG #concurrency :Broadcast to all 10

C1 EXPECT_CONNECTED
C10 EXPECT_CONNECTED
