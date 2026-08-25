# 43_MODE_ampersand_channel_prefix.spec
# Tests querying and modifying modes on channels with '&' prefix (e.g. &local)
# Expected: Server returns 324 RPL_CHANNELMODEIS and applies mode changes on &local channels.
# Bug: Server checks channel_name[0] != '#' and silently drops MODE on '&' channels.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali160
C1 SEND USER ali160 0 * :Ali160
C1 EXPECT 001 Ali160 :*

# Join '&' local channel
C1 SEND JOIN &local
C1 EXPECT 353 Ali160 = &local :@Ali160
C1 EXPECT 366 Ali160 &local :End of /NAMES list

# Query modes on '&' channel
C1 SEND MODE &local
C1 EXPECT 324 Ali160 &local +*

# Set invite-only mode on '&' channel
C1 SEND MODE &local +i
C1 EXPECT :Ali160!* MODE &local +i
