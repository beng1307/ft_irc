# 44_MODE_non_member_query.spec
# Tests querying channel modes as a non-member (e.g. MODE #public)
# Expected: Server returns 324 RPL_CHANNELMODEIS with the channel's modes.
# Bug: Server requires channel membership via ensure_channel_member and rejects non-members with 442 :You're not on that channel.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali161
C1 SEND USER ali161 0 * :Ali161
C1 EXPECT 001 Ali161 :*

C2 SEND PASS 1234
C2 SEND NICK Bob161
C2 SEND USER bob161 0 * :Bob161
C2 EXPECT 001 Bob161 :*

# Alice creates channel and sets it to topic restricted
C1 SEND JOIN #public
C1 EXPECT 353 Ali161 = #public :@Ali161
C1 EXPECT 366 Ali161 #public :End of /NAMES list
C1 SEND MODE #public +t
C1 EXPECT :Ali161!* MODE #public +t

# Bob (not in #public) queries channel modes
C2 SEND MODE #public
C2 EXPECT 324 Bob161 #public +*t*
