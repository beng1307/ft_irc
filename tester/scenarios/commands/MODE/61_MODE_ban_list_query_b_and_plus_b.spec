# 61_MODE_ban_list_query_b_and_plus_b.spec
# IRC Standard / Compatibility: Querying channel ban list with "MODE #chan b" and "MODE #chan +b".
# Expected: Server replies with 368 RPL_ENDOFBANLIST.
CLIENTS C1

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER alice 0 * :Alice
C1 EXPECT 001 Alice :*

C1 SEND JOIN #banquery
C1 EXPECT 353 Alice = #banquery :@Alice
C1 EXPECT 366 Alice #banquery :End of /NAMES list

# Query ban list with 'b'
C1 SEND MODE #banquery b
C1 EXPECT 368 Alice #banquery :End of Channel Ban List

# Query ban list with '+b'
C1 SEND MODE #banquery +b
C1 EXPECT 368 Alice #banquery :End of Channel Ban List
