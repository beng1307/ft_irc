# 78_INVITE_comma_separated_channel_rejection.spec
# Tests malformed / injection attempt with comma-separated channel lists in INVITE.
# Expected: Server does not split by comma, treats '#roomA,#roomB' as a literal channel name and returns 403 ERR_NOSUCHCHANNEL.
CLIENTS C1, C2

# Alice creates #roomA78 and #roomB78
C1 SEND PASS 1234
C1 SEND NICK Alice78
C1 SEND USER alice78 0 * :Alice
C1 EXPECT 001 Alice78 :*
C1 SEND JOIN #roomA78
C1 EXPECT :Alice78!* JOIN #roomA78
C1 SEND JOIN #roomB78
C1 EXPECT :Alice78!* JOIN #roomB78

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob78
C2 SEND USER bob78 0 * :Bob
C2 EXPECT 001 Bob78 :*

# Alice attempts batch invite with comma list
C1 SEND INVITE Bob78 #roomA78,#roomB78
C1 EXPECT 403 Alice78 #roomA78,#roomB78 :No such channel
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
