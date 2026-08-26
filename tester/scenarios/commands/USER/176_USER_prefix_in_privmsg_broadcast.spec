# 176_USER_prefix_in_privmsg_broadcast.spec
# Verifies that the username configured via USER is correctly reflected in PRIVMSG hostmasks
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali398
C1 SEND USER customuser 0 * :Custom Realname
C1 EXPECT 001 Ali398 :*
C1 EXPECT 002 Ali398 :*
C1 EXPECT 003 Ali398 :*
C1 EXPECT 004 Ali398 *

C2 SEND PASS 1234
C2 SEND NICK Bob398
C2 SEND USER bby398 0 * :Bob398
C2 EXPECT 001 Bob398 :*
C2 EXPECT 002 Bob398 :*
C2 EXPECT 003 Bob398 :*
C2 EXPECT 004 Bob398 *

C1 SEND JOIN #room03
C1 EXPECT :Ali398!customuser@localhost JOIN #room03
C1 EXPECT 331 Ali398 #room03 :No topic is set
C1 EXPECT 353 Ali398 = #room03 :@Ali398
C1 EXPECT 366 Ali398 #room03 :End of /NAMES list

C2 SEND JOIN #room03
C1 EXPECT :Bob398!bby398@localhost JOIN #room03
C2 EXPECT :Bob398!bby398@localhost JOIN #room03
C2 EXPECT 331 Bob398 #room03 :No topic is set
C2 EXPECT 353 Bob398 = #room03 :@Ali398 Bob398
C2 EXPECT 366 Bob398 #room03 :End of /NAMES list

C1 SEND PRIVMSG #room03 :hello everyone
C2 EXPECT :Ali398!customuser@localhost PRIVMSG #room03 :hello everyone
