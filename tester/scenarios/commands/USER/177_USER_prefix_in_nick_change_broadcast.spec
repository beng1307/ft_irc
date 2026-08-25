# 177_USER_prefix_in_nick_change_broadcast.spec
# Verifies that username is preserved when a user changes nickname post-registration
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali399
C1 SEND USER ali399 0 * :Ali399 Keys
C1 EXPECT 001 Ali399 :*
C1 EXPECT 002 Ali399 :*
C1 EXPECT 003 Ali399 :*
C1 EXPECT 004 Ali399 *

C2 SEND PASS 1234
C2 SEND NICK Bob399
C2 SEND USER bby399 0 * :Bob399 Builder
C2 EXPECT 001 Bob399 :*
C2 EXPECT 002 Bob399 :*
C2 EXPECT 003 Bob399 :*
C2 EXPECT 004 Bob399 *

C1 SEND JOIN #room
C1 EXPECT :Ali399!ali399@localhost JOIN #room
C1 EXPECT 331 Ali399 #room :No topic is set
C1 EXPECT 353 Ali399 = #room :@Ali399
C1 EXPECT 366 Ali399 #room :End of /NAMES list

C2 SEND JOIN #room
C1 EXPECT :Bob399!bby399@localhost JOIN #room
C2 EXPECT :Bob399!bby399@localhost JOIN #room
C2 EXPECT 331 Bob399 #room :No topic is set
C2 EXPECT 353 Bob399 = #room :@Ali399 Bob399
C2 EXPECT 366 Bob399 #room :End of /NAMES list

C1 SEND NICK AliciaNew
C2 EXPECT :Ali399!ali399@localhost NICK :AliciaNew
C1 EXPECT :Ali399!ali399@localhost NICK :AliciaNew
