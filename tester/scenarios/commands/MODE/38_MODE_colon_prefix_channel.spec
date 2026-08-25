# 38_MODE_colon_prefix_channel.spec
# Tests RFC colon-prefixed channel name and mode string (e.g., MODE :#chan, MODE #chan :+i)
# Expected: Server parses channel name and mode string correctly, returning 324 RPL_CHANNELMODEIS or broadcasting mode change.
# Bug: Server checks chan[0] != '#' rejecting ':#chan', and fails to strip ':' from ':+i', triggering 472 : :is unknown mode char to me.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Create channel
C1 SEND JOIN #chan
C1 EXPECT 353 Alice = #chan :@Alice
C1 EXPECT 366 Alice #chan :End of /NAMES list

# Query modes using colon prefix
C1 SEND MODE :#chan
C1 EXPECT 324 Alice #chan +*

# Set mode using colon-prefixed mode string
C1 SEND MODE #chan :+i
C1 EXPECT :Alice!* MODE #chan +i
