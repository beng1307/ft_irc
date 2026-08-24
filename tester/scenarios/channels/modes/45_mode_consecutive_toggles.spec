# MODE toggled on and off repeatedly in single command.
# Example: +i-i+i should result in +i.
# Tests mode normalization logic.

CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #togglechannel
C1 EXPECT :Alice!* JOIN #togglechannel

# Set initial state
C1 SEND MODE #togglechannel +i
C1 EXPECT :Alice!* MODE #togglechannel +i

# Toggle multiple times in one command: +i-i+i
# Should result in +i (final state is ON)
C1 SEND MODE #togglechannel +i-i+i
# Server should normalize this
C1 EXPECT_CONNECTED

# Query mode to see final state
C1 SEND MODE #togglechannel
C1 EXPECT 324 Alice #togglechannel +i

# Clear the mode
C1 SEND MODE #togglechannel -i
C1 EXPECT :Alice!* MODE #togglechannel -i

# Toggle starting from OFF: -i+i-i
# Should result in -i (final state is OFF)
C1 SEND MODE #togglechannel -i+i-i
C1 EXPECT_CONNECTED

# Query final state
C1 SEND MODE #togglechannel
C1 EXPECT 324 Alice #togglechannel *

C1 EXPECT_CONNECTED
