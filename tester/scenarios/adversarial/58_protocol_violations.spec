# Protocol violation and malformed command handling
# Tests server resilience to various protocol violations

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Test 1: Completely garbage input
C1 SEND @#$%^&*()
C1 EXPECT_CONNECTED

# Test 2: Command with way too many parameters
C1 SEND PRIVMSG #test param1 param2 param3 param4 param5 :message
C1 EXPECT_CONNECTED

# Test 3: Empty command
C1 SEND 
C1 EXPECT_CONNECTED

# Test 4: Whitespace-only command
C1 SEND    
C1 EXPECT_CONNECTED

# Test 5: Command with trailing spaces
C1 SEND NICK Alice  
C1 EXPECT_CONNECTED

# Test 6: PRIVMSG to channel with rapid messages
C1 SEND JOIN #channel
C1 EXPECT :Alice!* JOIN #channel
C2 SEND JOIN #channel
C2 EXPECT :Bob!* JOIN #channel

# C2 sends messages rapidly
C2 SEND PRIVMSG #channel :msg1
C2 SEND PRIVMSG #channel :msg2
C2 SEND PRIVMSG #channel :msg3
C2 SEND PRIVMSG #channel :msg4
C2 SEND PRIVMSG #channel :msg5

# C1 receives messages
C1 EXPECT :Bob!* PRIVMSG #channel :msg1
C1 EXPECT :Bob!* PRIVMSG #channel :msg2
C1 EXPECT :Bob!* PRIVMSG #channel :msg3
C1 EXPECT :Bob!* PRIVMSG #channel :msg4
C1 EXPECT :Bob!* PRIVMSG #channel :msg5

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
