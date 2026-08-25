# PRIVMSG with special characters: tabs, multiple spaces, and printable control chars.
# Ensures server doesn't mangle or reject valid IRC messages.

CLIENTS C1, C2

C1 SEND PASS 1234
C1 SEND NICK Ali432
C1 SEND USER ali432 0 * :Ali432
C1 EXPECT 001 Ali432 :*

C2 SEND PASS 1234
C2 SEND NICK Bob432
C2 SEND USER bob432 0 * :Bob432
C2 EXPECT 001 Bob432 :*

# Message with leading/trailing spaces
C1 SEND PRIVMSG Bob432 :   spaced message   
C2 WAIT_RECV :Ali432!* PRIVMSG Bob432 :   spaced message   

# Message with tabs (should be preserved)
C1 SEND PRIVMSG Bob432 :hello	world	tab
C2 WAIT_RECV :Ali432!* PRIVMSG Bob432 :hello	world	tab

# Message with punctuation
C1 SEND PRIVMSG Bob432 :!@#$%^&*()_+-={}[];'<>?,./~`
C2 WAIT_RECV :Ali432!* PRIVMSG Bob432 :!@#$%^&*()_+-={}[];'<>?,./~`

C1 EXPECT_CONNECTED
C2 EXPECT_CONNECTED
