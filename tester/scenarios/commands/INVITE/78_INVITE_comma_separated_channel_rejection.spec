# 78_INVITE_comma_separated_channel_rejection.spec
# Tests malformed / injection attempt with comma-separated channel lists in INVITE.
# Expected: Server does not split by comma, treats '#roomA,#roomB' as a literal channel name and returns 403 ERR_NOSUCHCHANNEL.
CLIENTS C1, C2

# Alice creates #roomA78 and #roomB78
C1 SEND PASS 1234
C1 SEND NICK Ali103
C1 SEND USER ali103 0 * :Ali103
C1 EXPECT 001 Ali103 :*
C1 SEND JOIN #roomA78
C1 EXPECT :Ali103!* JOIN #roomA78
C1 SEND JOIN #roomB78
C1 EXPECT :Ali103!* JOIN #roomB78

# Bob registers
C2 SEND PASS 1234
C2 SEND NICK Bob103
C2 SEND USER bob103 0 * :Bob103
C2 EXPECT 001 Bob103 :*

# Alice attempts batch invite with comma list
C1 SEND INVITE Bob103 #roomA78,#roomB78
C1 EXPECT 403 Ali103 #roomA78,#roomB78 :No such channel
C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
