# Message delivery and buffering under stress
# Tests server behavior with rapid messages and slow clients

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Create channel
C1 SEND JOIN #stress
C1 EXPECT :Alice!* JOIN #stress
C2 SEND JOIN #stress
C2 EXPECT :Bob!* JOIN #stress

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
C2 EXPECT :Alice!* PRIVMSG #stress :msg001
C2 EXPECT :Alice!* PRIVMSG #stress :msg002
C2 EXPECT :Alice!* PRIVMSG #stress :msg003
C2 EXPECT :Alice!* PRIVMSG #stress :msg004
C2 EXPECT :Alice!* PRIVMSG #stress :msg005

# Test 2: Server should not crash or disconnect
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED

# Test 3: Private messages with rapid fire
C1 SEND PRIVMSG Bob :priv001
C1 SEND PRIVMSG Bob :priv002
C1 SEND PRIVMSG Bob :priv003
C1 SEND PRIVMSG Bob :priv004
C1 SEND PRIVMSG Bob :priv005

C2 EXPECT :Alice!* PRIVMSG Bob :priv001
C2 EXPECT :Alice!* PRIVMSG Bob :priv002
C2 EXPECT :Alice!* PRIVMSG Bob :priv003
C2 EXPECT :Alice!* PRIVMSG Bob :priv004
C2 EXPECT :Alice!* PRIVMSG Bob :priv005

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
