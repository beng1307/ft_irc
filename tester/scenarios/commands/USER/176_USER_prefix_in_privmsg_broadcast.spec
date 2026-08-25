# 176_USER_prefix_in_privmsg_broadcast.spec
# Verifies that the username configured via USER is correctly reflected in PRIVMSG hostmasks
CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Alice
C1 SEND USER customuser 0 * :Custom Realname
C1 EXPECT 001 Alice :*
C1 EXPECT 002 Alice :*
C1 EXPECT 003 Alice :*
C1 EXPECT 004 Alice *

C2 SEND PASS 1234
C2 SEND NICK Bob
C2 SEND USER bobby 0 * :Bob
C2 EXPECT 001 Bob :*
C2 EXPECT 002 Bob :*
C2 EXPECT 003 Bob :*
C2 EXPECT 004 Bob *

C1 SEND JOIN #room
C1 EXPECT :Alice!customuser@localhost JOIN #room
C1 EXPECT 331 Alice #room :No topic is set
C1 EXPECT 353 Alice = #room :@Alice
C1 EXPECT 366 Alice #room :End of /NAMES list

C2 SEND JOIN #room
C1 EXPECT :Bob!bobby@localhost JOIN #room
C2 EXPECT :Bob!bobby@localhost JOIN #room
C2 EXPECT 331 Bob #room :No topic is set
C2 EXPECT 353 Bob = #room :@Alice Bob
C2 EXPECT 366 Bob #room :End of /NAMES list

C1 SEND PRIVMSG #room :hello everyone
C2 EXPECT :Alice!customuser@localhost PRIVMSG #room :hello everyone
