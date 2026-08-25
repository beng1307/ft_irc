# 22_JOIN_colon_prefix.spec
# Tests RFC trailing colon notation on channel name parameter (e.g. JOIN :#chan)
# Expected: Server strips leading colon and joins the client to #chan with JOIN broadcast and 353/366 replies.
# Bug: Server checks chan[0] != '#' and rejects ':#chan' with 403 :#chan :No such channel.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Ali105
C1 SEND USER ali105 0 * :Ali105
C1 EXPECT 001 Ali105 :*

# Join channel using colon prefix
C1 SEND JOIN :#chan
C1 EXPECT :Ali105!* JOIN #chan
C1 EXPECT 353 Ali105 = #chan :*Ali105*
C1 EXPECT 366 Ali105 #chan :End of /NAMES list
