# 22_JOIN_colon_prefix.spec
# Tests RFC trailing colon notation on channel name parameter (e.g. JOIN :#chan)
# Expected: Server strips leading colon and joins the client to #chan with JOIN broadcast and 353/366 replies.
# Bug: Server checks chan[0] != '#' and rejects ':#chan' with 403 :#chan :No such channel.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

# Join channel using colon prefix
C1 SEND JOIN :#chan
C1 EXPECT :Alice!* JOIN #chan
C1 EXPECT 353 Alice = #chan :*Alice*
C1 EXPECT 366 Alice #chan :End of /NAMES list
