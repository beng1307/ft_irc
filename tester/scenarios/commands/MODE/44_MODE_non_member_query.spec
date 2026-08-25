# 44_MODE_non_member_query.spec
# Tests querying channel modes as a non-member (e.g. MODE #public)
# Expected: Server returns 324 RPL_CHANNELMODEIS with the channel's modes.
# Bug: Server requires channel membership via ensure_channel_member and rejects non-members with 442 :You're not on that channel.
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bob 0 * :Bob
C2 EXPECT 001 Bob :*

# Alice creates channel and sets it to topic restricted
C1 SEND JOIN #public
C1 EXPECT 353 Alice = #public :@Alice
C1 EXPECT 366 Alice #public :End of /NAMES list
C1 SEND MODE #public +t
C1 EXPECT :Alice!* MODE #public +t

# Bob (not in #public) queries channel modes
C2 SEND MODE #public
C2 EXPECT 324 Bob #public +*t*
