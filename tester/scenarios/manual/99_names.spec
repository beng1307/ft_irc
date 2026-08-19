# Validates simultaneous multiplexing across 10 concurrent active client connections.
CLIENTS C1, C2

# Register all 10 clients concurrently
C1 SEND PASS 1234
C1 SEND NICK User1
C1 SEND USER u1 0 * :User One


C2 SEND PASS 1234
C2 SEND NICK User2
C2 SEND USER u2 0 * :User Two



C1 SEND JOIN #test
WAIT 200ms
C2 SEND JOIN #test

C1 EXPECT 353 * :*