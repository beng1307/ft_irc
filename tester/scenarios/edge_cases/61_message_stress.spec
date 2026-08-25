# Message delivery and buffering under stress
# Tests server behavior with rapid messages and slow clients

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali416
C1 SEND USER ali416 0 * :Ali416
C1 EXPECT 001 Ali416 :*

C2 SEND PASS 1234
C2 SEND NICK Bob416
C2 SEND USER bob416 0 * :Bob416
C2 EXPECT 001 Bob416 :*

# Create channel
C1 SEND JOIN #stress
C1 EXPECT :Ali416!* JOIN #stress
C2 SEND JOIN #stress
C2 EXPECT :Bob416!* JOIN #stress

# Test 1: Rapid fire PRIVMSG (100 messages)
C1 SEND PRIVMSG #stress :msg001
C1 SEND PRIVMSG #stress :msg002
C1 SEND PRIVMSG #stress :msg003
C1 SEND PRIVMSG #stress :msg004
C1 SEND PRIVMSG #stress :msg005
C1 SEND PRIVMSG #stress :msg006
C1 SEND PRIVMSG #stress :msg007
C1 SEND PRIVMSG #stress :msg008
C1 SEND PRIVMSG #stress :msg009
C1 SEND PRIVMSG #stress :msg010
C1 SEND PRIVMSG #stress :msg011
C1 SEND PRIVMSG #stress :msg012
C1 SEND PRIVMSG #stress :msg013
C1 SEND PRIVMSG #stress :msg014
C1 SEND PRIVMSG #stress :msg015
C1 SEND PRIVMSG #stress :msg016
C1 SEND PRIVMSG #stress :msg017
C1 SEND PRIVMSG #stress :msg018
C1 SEND PRIVMSG #stress :msg019
C1 SEND PRIVMSG #stress :msg020

# Receiver should get all messages (or at least the first few before buffer fills)
C2 EXPECT :Ali416!* PRIVMSG #stress :msg001
C2 EXPECT :Ali416!* PRIVMSG #stress :msg002
C2 EXPECT :Ali416!* PRIVMSG #stress :msg003
C2 EXPECT :Ali416!* PRIVMSG #stress :msg004
C2 EXPECT :Ali416!* PRIVMSG #stress :msg005

# Test 2: Server should not crash or disconnect
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED

# Test 3: Private messages with rapid fire
C1 SEND PRIVMSG Bob416 :priv001
C1 SEND PRIVMSG Bob416 :priv002
C1 SEND PRIVMSG Bob416 :priv003
C1 SEND PRIVMSG Bob416 :priv004
C1 SEND PRIVMSG Bob416 :priv005

C2 EXPECT :Ali416!* PRIVMSG Bob416 :priv001
C2 EXPECT :Ali416!* PRIVMSG Bob416 :priv002
C2 EXPECT :Ali416!* PRIVMSG Bob416 :priv003
C2 EXPECT :Ali416!* PRIVMSG Bob416 :priv004
C2 EXPECT :Ali416!* PRIVMSG Bob416 :priv005

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
