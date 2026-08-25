# Validates simultaneous multiplexing across 10 concurrent active client connections.
CLIENTS C1, C2

# Register all 10 clients concurrently
C1 SEND PASS 1234
C1 SEND NICK Usr426
C1 SEND USER u1_499 0 * :Usr426 One


C2 SEND PASS 1234
C2 SEND NICK Usr426
C2 SEND USER u2_499 0 * :Usr426 Two



C1 SEND JOIN #test
WAIT 200ms
C2 SEND JOIN #test

C1 EXPECT 353 * :*