# 38_MODE_colon_prefix_channel.spec
# Tests RFC colon-prefixed channel name and mode string (e.g., MODE :#chan, MODE #chan :+i)
# Expected: Server parses channel name and mode string correctly, returning 324 RPL_CHANNELMODEIS or broadcasting mode change.
# Bug: Server checks chan[0] != '#' rejecting ':#chan', and fails to strip ':' from ':+i', triggering 472 : :is unknown mode char to me.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali155
C1 SEND USER ali155 0 * :Ali155
C1 EXPECT 001 Ali155 :*

# Create channel
C1 SEND JOIN #chan
C1 EXPECT 353 Ali155 = #chan :@Ali155
C1 EXPECT 366 Ali155 #chan :End of /NAMES list

# Query modes using colon prefix
C1 SEND MODE :#chan
C1 EXPECT 324 Ali155 #chan +*

# Set mode using colon-prefixed mode string
C1 SEND MODE #chan :+i
C1 EXPECT :Ali155!* MODE #chan +i
